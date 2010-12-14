from collections import defaultdict
import csv
from operator import itemgetter
import datetime
import itertools

try:
    import json
except ImportError:
    import simplejson as json

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db.models import *
from django.views.generic.list_detail import object_detail
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import Http404, HttpResponse

from dateutil.relativedelta import relativedelta

from willard.models import *


def index(request):
    registrations = Registration.objects.filter(received__lte=datetime.date.today(), received__gte=datetime.date.today()-relativedelta(months=1)).select_related()
    registrations_by_date = [{'date': date, 'registrations': list(regs)} for date, regs in itertools.groupby(registrations, lambda x: x.received.date())][:5]

    top_issue_ids = Issue.objects.values_list('pk', flat=True).order_by('-registration_count')[:5]
    top_issues = Issue.objects.filter(pk__in=list(top_issue_ids))

    issues_by_month = {}
    for issue in top_issues:
        issues_by_month[issue] = issue.issuebymonth_set.values('year', 'month', 'num')

    months = []
    cutoff = datetime.date.today() - relativedelta(months=12)
    cutoff = datetime.date(year=cutoff.year, month=cutoff.month, day=1)

    past_year_count = Registration.objects.filter(received__gte=cutoff).count()

    # Create a list of registrations by month for the past year.
    registrations_by_month = itertools.groupby(Registration.objects.filter(received__lte=datetime.date.today(),
                                                                           received__gte=cutoff).order_by('received'),
                                               lambda x: {'month': x.received.month,
                                                          'year': x.received.year, 
                                                          'month_initial': x.received.strftime('%B')[0],
                                                          'month_name': x.received.strftime('%B'),
                                                          })
    # Iterate over registrations_by_month
    registrations_by_month = [(month, len(list(registrations))) for month, registrations in registrations_by_month]

    # Create a list of registrations by day for the 30 days previous to the last registration.
    last_date = Registration.objects.order_by('-received').values_list('received', flat=True)[0].date()
    month_cutoff = last_date - datetime.timedelta(30)
    registrations_by_day = dict()
    for date, group in itertools.groupby(Registration.objects.filter(received__gte=month_cutoff).values_list('received', flat=True), lambda x: x.date()):
        registrations_by_day[date] = len(list(group))

    # Fill in any missing dates with 0
    curr = month_cutoff
    while curr <= last_date:
        if curr not in registrations_by_day:
            registrations_by_day[curr] = 0
        curr += datetime.timedelta(1)

    registrations_by_day = sorted(registrations_by_day.items(), key=itemgetter(0))

    return render_to_response('willard/index.html',
                              {'object_list': registrations_by_date,
                               'months': months,
                               'issues': Issue.objects.filter(registration__received__gte=cutoff).annotate(num=Count('registration')).order_by('-num').select_related(),
                               'past_month_issues': Issue.objects.filter(registration__received__gte=month_cutoff).annotate(num=Count('registration')).order_by('-num').select_related(),
                               'past_year_count': past_year_count,
                               'past_month_count': sum([x[1] for x in registrations_by_day]),
                               'registrations_by_month': registrations_by_month,
                               'registrations_by_day': registrations_by_day,
                                },
                              context_instance=RequestContext(request))


def issue_detail(request, slug):
    issue = get_object_or_404(Issue, slug=slug)

    order, given_order = generic_pagination(request)
    registrations = issue.registration_set.order_by(*order).select_related()
    page = make_paginator(request, registrations)

    #registrations = issue.registration_set.order_by('-received').select_related()[:25]

    cutoff = datetime.date.today() - relativedelta(months=12)
    cutoff = datetime.date(year=cutoff.year,
                           month=cutoff.month,
                           day=1)

    # Get month counts for the past 12 months.
    regs = issue.registration_set.filter(received__gte=cutoff).values('received')
    grouped = itertools.groupby(regs, lambda x: {'year': x['received'].year, 'month': x['received'].month})
    month_counts = [{'year': date['year'], 'month': date['month'], 'count': len(list(group))} for date, group in grouped]
    month_counts.reverse()

    # Get top registrants for this issue over the past 12 months.
    org_counts = issue.registration_set.filter(received__gte=cutoff).values_list('registrant').annotate(num=Count('pk')).filter(num__gte=5).order_by('-num')[:20]
    counts = dict(org_counts)
    orgs = Registrant.objects.filter(pk__in=[x[0] for x in org_counts])
    for org in orgs:
        org.num = counts[org.pk]
    orgs = sorted(list(orgs), lambda x, y: cmp(x.num, y.num), reverse=True)

    return render_to_response('willard/issue_detail.html',
                              {'issue': issue,
                               'month_counts': month_counts,
                               'top_registrants': orgs,
                               'past_year_count': sum(counts.values()),
                               'order': given_order.strip('-'),
                               'sort': 'desc' if given_order.startswith('-') else 'asc',
                               'given_order': given_order,
                               'object_list': page.object_list,
                               'page_obj': page,
                               },
                              context_instance=RequestContext(request))


def detail_api(request, model, slug, format):
    obj = get_object_or_404(model, slug=slug)
    registrations = obj.registration_set.order_by('-received').select_related()
    data = {model._meta.verbose_name: obj.__unicode__(),
            'path': obj.get_absolute_url(),
            'registrations': [], }
    return registrations_api(registrations, format, data)


def registrations_api(registrations, format, data):
    allowed_formats = ('csv', 'json', )
    if format not in allowed_formats:
        raise Http404

    if format == 'json':
        for registration in registrations:
            data['registrations'].append(registration.as_dict())

        return HttpResponse(json.dumps(data), mimetype='text/plain')

    elif format == 'csv':
        response = HttpResponse(mimetype='text/plain')
        writer = csv.writer(response)
        headers = ['senate_id',
                   'registration_type',
                   'client',
                   'received',
                   'issues',
                   'specific_issue', ]

        rows = [headers, ] + [x.as_csv() for x in registrations]

        writer.writerows(rows)
        return response




def generic_pagination(request):
    order_options = ('received',
                     'registrant',
                     'client', )

    default_order = '-received'
    given_order = request.GET.get('order', default_order)
    if given_order.strip('-') not in order_options:
        given_order = default_order

    if given_order == 'registrant':
        order = ('registrant__crp_name', 'registrant__name')
    elif given_order == '-registrant':
        order = ('-registrant__crp_name', '-registrant__name')
    elif given_order == 'client':
        order = ('client__crp_name', 'client__name')
    elif given_order == '-client':
        order = ('-client__crp_name', '-client__name')
    else:
        order = (given_order,)

    return order, given_order


def make_paginator(request, object_list):
    paginator = Paginator(object_list, 50, orphans=5)
    pagenum = request.GET.get('page', 1)
    try:
        page = paginator.page(pagenum)
    except (EmptyPage, InvalidPage):
        raise Http404
    return page


def issue_detail_all(request, slug):
    issue = get_object_or_404(Issue, slug=slug)
    order, given_order = generic_pagination(request)
    registrations = issue.registration_set.order_by(*order).select_related()
    page = make_paginator(request, registrations)

    return render_to_response('willard/issue_detail_all.html',
                              {'object_list': page.object_list,
                               'issue': issue,
                               'order': given_order.strip('-'),
                               'sort': 'desc' if given_order.startswith('-') else 'asc',
                               'given_order': given_order,
                               'page_obj': page,
                              }, context_instance=RequestContext(request))


def registrations_all(request):
    order, given_order = generic_pagination(request)
    registrations = Registration.objects.order_by(*order).select_related()
    page = make_paginator(request, registrations)

    return render_to_response('willard/registration_list.html',
                              {'object_list': page.object_list,
                               'page_obj': page,
                               'order': given_order.strip('-'),
                               'given_order': given_order,
                               'sort': 'desc' if given_order.startswith('-') else 'asc',
                              }, context_instance=RequestContext(request))

def generic_detail_all(request, model, slug):
    obj = get_object_or_404(model, slug=slug)
    order, given_order = generic_pagination(request)
    registrations = obj.registration_set.order_by(*order).select_related()
    page = make_paginator(request, registrations)

    return render_to_response('willard/registration_list.html',
                              {'object_list': page.object_list,
                               'page_obj': page,
                               'order': given_order.strip('-'),
                               'given_order': given_order,
                               'sort': 'desc' if given_order.startswith('-') else 'asc',
                               'object': obj,
                               'plural': model._meta.verbose_name_plural.title(),
                              }, context_instance=RequestContext(request))


def registration_detail(request, slug, id):
    registrant = get_object_or_404(Registrant, slug=slug)
    registration = get_object_or_404(Registration, id=id, registrant=registrant)

    return object_detail(request,
                         Registration.objects.all(),
                         object_id=registration.pk)


def registrant_detail(request, slug):
    registrants = Registrant.objects.filter(slug=slug) # Multiple registrants could have the same slug
    if not registrants:
        raise Http404
    registrations = Registration.objects.filter(registrant__slug=slug).select_related()

    return render_to_response('willard/registrant_detail.html',
                              {'registrant': registrants[0],
                               'registrants': registrants,
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


def search(request):
    term = request.GET.get('q', None)

    if term:
        registrants = Registrant.objects.filter(display_name__icontains=term)
        clients = Client.objects.filter(display_name__icontains=term)
    else:
        registrants = None
        clients = None

    num_results = registrants.count() + clients.count()

    return render_to_response('willard/search.html',
                              {'registrants': registrants,
                               'clients': clients,
                               'term': term, 
                               'num_results': num_results,
                               },
                              context_instance=RequestContext(request))
