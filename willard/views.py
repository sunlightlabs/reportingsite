from collections import defaultdict
import datetime
import itertools

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db.models import *
from django.views.generic.list_detail import object_detail
from django.core.paginator import Paginator, EmptyPage, InvalidPage

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
                               'issues': IssueCode.objects.exclude(issue='').order_by('issue'),
                                },
                              context_instance=RequestContext(request))


def issue_detail(request, code):
    issue_code = get_object_or_404(IssueCode, code=code)
    registrations = issue_code.registration_set.all()

    paginator = Paginator(registrations, 50, orphans=5)
    pagenum = request.GET.get('page', 1)
    try:
        page = paginator.page(pagenum)
    except (EmptyPage, InvalidPage):
        raise Http404

    """
    min_date = Registration.objects.exclude(signed_date=None).order_by('signed_date').values_list('signed_date', flat=True)[0]
    max_date = datetime.date.today()

    year_groups = itertools.groupby(registrations, key=lambda x: x.signed_date.year)
    date_data = []
    for year, regs in year_groups:
        month_groups = itertools.groupby(regs, key=lambda x: x.signed_date.month)
        for month, month_registrations in month_groups:
            date = datetime.date(2010, month, 1)
            date_data.append((date, list(month_registrations)))
    """

    # Get month counts for the past 12 months.
    month_counts = []
    curr = datetime.date.today()
    while len(month_counts) < 12:
        month_counts.append({'month': curr.month, 'year': curr.year, 'count': registrations.filter(signed_date__year=curr.year, signed_date__month=curr.month).count()})
        curr -= relativedelta(months=1)
    month_counts.reverse()

    # Get top registrants for this issue over the past 12 months.
    cutoff = datetime.date.today() - relativedelta(months=12)
    cutoff = datetime.date(year=cutoff.year,
                           month=cutoff.month,
                           day=1)
    org_counts = issue_code.registration_set.filter(signed_date__gte=cutoff).values('organization').annotate(c=Count('pk')).order_by('-c')[:5]
    orgs = Organization.objects.filter(pk__in=[x['organization'] for x in org_counts])

    return render_to_response('willard/issuecode_detail.html',
                              {'issue_code': issue_code,
                               #'date_data': date_data,
                               'month_counts': month_counts,
                               'page_obj': page,
                               'top_registrants': orgs,
                               #'dates': dates,
                               },
                              context_instance=RequestContext(request))


def registration_detail(request, slug, form_id):
    organization = get_object_or_404(Organization, slug=slug)
    registration = get_object_or_404(Registration, form_id=form_id, organization=organization)

    return object_detail(request,
                         Registration.objects.all(),
                         object_id=registration.pk)
