from collections import defaultdict
import datetime
import itertools

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db.models import *
from django.views.generic.list_detail import object_detail
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import Http404

from dateutil.relativedelta import relativedelta

from willard.models import *


def index(request):
    registrations = Registration.objects.filter(signed_date__lte=datetime.date.today(), signed_date__gte=datetime.date.today()-relativedelta(months=1)).select_related()
    registrations_by_date = [{'date': date, 'registrations': list(regs)} for date, regs in itertools.groupby(registrations, lambda x: x.signed_date)][:10]

    top_issue_ids = IssueCode.objects.values_list('pk', flat=True).order_by('-registration_count')[:5]
    top_issues = IssueCode.objects.filter(pk__in=list(top_issue_ids))

    issues_by_month = {}
    for issue in top_issues:
        issues_by_month[issue] = issue.issuecodebymonth_set.values('year', 'month', 'num')

    months = []
    cutoff = datetime.date.today() - relativedelta(months=11)
    cutoff = datetime.date(year=cutoff.year,
                           month=cutoff.month,
                           day=1)
    curr = cutoff
    issue_counts = defaultdict(list)
    while curr <= datetime.date.today():
        months.append(curr.strftime('%b')[0])
        for issue, by_month in issues_by_month.items():
            issue_counts[issue.issue].append(sum([x['num'] for x in by_month if x['year'] == str(curr.year) and x['month'] == str(curr.month)]))

        curr += relativedelta(months=1)

    return render_to_response('willard/index.html',
                              {'object_list': registrations_by_date,
                               'issue_counts': issue_counts.items(),
                               'months': months,
                               #'issues': IssueCode.objects.exclude(issue='').order_by('issue'),
                               'issues': IssueCode.objects.filter(registration__signed_date__gte=cutoff).annotate(num=Count('registration')).order_by('-num').select_related(),
                               'past_year_count': sum([x['num'] for x in by_month]),
                                },
                              context_instance=RequestContext(request))


def issue_detail(request, code):
    issue_code = get_object_or_404(IssueCode, code=code)
    registrations = issue_code.registration_set.all().select_related()

    paginator = Paginator(registrations, 50, orphans=5)
    pagenum = request.GET.get('page', 1)
    try:
        page = paginator.page(pagenum)
    except (EmptyPage, InvalidPage):
        raise Http404

    cutoff = datetime.date.today() - relativedelta(months=11)
    cutoff = datetime.date(year=cutoff.year,
                           month=cutoff.month,
                           day=1)

    # Get month counts for the past 12 months.
    regs = issue_code.registration_set.filter(signed_date__gte=cutoff).values('signed_date')
    grouped = itertools.groupby(regs, lambda x: {'year': x['signed_date'].year, 'month': x['signed_date'].month})
    month_counts = [{'year': date['year'], 'month': date['month'], 'count': len(list(group))} for date, group in grouped]
    month_counts.reverse()

    # Get top registrants for this issue over the past 12 months.
    org_counts = issue_code.registration_set.filter(signed_date__gte=cutoff).values_list('organization').annotate(num=Count('pk')).order_by('-num')[:15]
    counts = dict(org_counts)
    orgs = Organization.objects.filter(pk__in=[x[0] for x in org_counts])
    for org in orgs:
        org.num = counts[org.pk]
    orgs = sorted(list(orgs), lambda x, y: cmp(x.num, y.num), reverse=True)

    return render_to_response('willard/issuecode_detail.html',
                              {'issue_code': issue_code,
                               'month_counts': month_counts,
                               'page_obj': page,
                               'top_registrants': orgs,
                               'past_year_count': sum(counts.values()),
                               },
                              context_instance=RequestContext(request))


def registration_detail(request, slug, form_id):
    organization = get_object_or_404(Organization, slug=slug)
    registration = get_object_or_404(Registration, form_id=form_id, organization=organization)

    return object_detail(request,
                         Registration.objects.all(),
                         object_id=registration.pk)


def organization_detail(request, slug):
    organizations = Organization.objects.filter(slug=slug)
    if not organizations:
        raise Http404
    registrations = Registration.objects.filter(organization__slug=slug).select_related()

    return render_to_response('willard/organization_detail.html',
                              {'organization': organizations[0],
                               'organizations': organizations,
                               'object_list': registrations,
                               },
                               context_instance=RequestContext(request))


def client_detail(request, slug):
    clients = Client.objects.filter(slug=slug)
    if not clients:
        raise Http404
    registrations = Registration.objects.filter(client__slug=slug).select_related()

    return render_to_response('willard/client_detail.html',
                              {'client': clients[0],
                               'clients': clients,
                               'object_list': registrations,
                              },
                              context_instance=RequestContext(request))
