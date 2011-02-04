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
    registrations = Registration.objects.filter(received__lte=datetime.date.today()).select_related()[:3]
    registrations_by_date = [{'date': date, 'registrations': list(regs)} for date, regs in itertools.groupby(registrations, lambda x: x.received.date())]

    postemployment = PostEmploymentNotice.objects.filter(end_date__gte=datetime.date.today()).order_by('end_date')[:5]
    postemployment_by_date = [{'date': date, 'notices': list(notices)} for date, notices in itertools.groupby(postemployment, lambda x: x.end_date)]
    print postemployment_by_date

    return render_to_response('willard/index.html',
                              {'registrations': registrations_by_date,
                               'postemployment': postemployment_by_date,
                              },
                              context_instance=RequestContext(request))


def registrations(request):
    registrations = Registration.objects.filter(received__lte=datetime.date.today(), received__gte=datetime.date.today()-relativedelta(months=1)).select_related()[:15]
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

    return render_to_response('willard/registrations.html',
                              {'object_list': registrations_by_date,
                               'months': months,
                               'issues': Issue.objects.filter(registration__received__gte=cutoff).annotate(num=Count('registration')).order_by('-num').select_related(),
                               'past_month_issues': Issue.objects.filter(registration__received__gte=month_cutoff).annotate(num=Count('registration')).order_by('-past_month_count').select_related(),
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
    past_year_count = sum([x['count'] for x in month_counts])

    # Get top registrants for this issue over the past 12 months.
    org_counts = issue.registration_set.filter(received__gte=cutoff).values_list('registrant').annotate(num=Count('pk')).filter(num__gte=5).order_by('-num')[:20]
    counts = dict(org_counts)
    if len(org_counts) > 1:
        orgs = Registrant.objects.filter(pk__in=[x[0] for x in org_counts])
        for org in orgs:
            org.num = counts[org.pk]
        orgs = sorted(list(orgs), lambda x, y: cmp(x.num, y.num), reverse=True)[:10]
    else:
        orgs = []

    return render_to_response('willard/issue_detail.html',
                              {'issue': issue,
                               'month_counts': month_counts,
                               'top_registrants': orgs,
                               'past_year_count': past_year_count,
                               'order': given_order.strip('-'),
                               'sort': 'desc' if given_order.startswith('-') else 'asc',
                               'given_order': given_order,
                               'object_list': page.object_list,
                               'page_obj': page,
                               },
                              context_instance=RequestContext(request))

def object_list_api(request, model, format):
    allowed_formats = ('csv', 'json', )
    if format not in allowed_formats:
        raise Http404

    object_list = []
    for obj in model.objects.all():
        object_list.append({'name': obj.display_name,
                            'url': obj.get_absolute_url(),
                            'slug': obj.slug,
                            'transparencydata_id': obj.ie_id(), })

    if format == 'json':
        return HttpResponse(json.dumps(object_list), mimetype='text/plain')

    elif format == 'csv':
        response = HttpResponse(mimetype='text/plain')
        fieldnames = ['name', 'slug', 'url', 'transparencydata_id', ]
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writerow(dict(zip(fieldnames, fieldnames)))
        writer.writerows(object_list)
        return response


def willard_postemployment_api(request, format):
    allowed_formats = ('csv', 'json', )
    if format not in allowed_formats:
        raise Http404

    object_list = []
    for obj in PostEmploymentNotice.objects.all():
        object_list.append({'last': obj.last,
                            'first': obj.first,
                            'middle': obj.middle,
                            'body': obj.body,
                            'office': obj.office_name,
                            'restriction_start': obj.begin_date,
                            'restriction_end': obj.end_date,
                            })

    if format == 'json':
        return HttpResponse(json.dumps(object_list), mimetype='text/plain')

    elif format == 'csv':
        response = HttpResponse(mimetype='text/plain')
        fieldnames = ['last', 'first', 'middle', 'body',
                        'office', 'restriction_start', 'restriction_end', ]
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writerow(dict(zip(fieldnames, fieldnames)))
        writer.writerows(object_list)
        return response


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
                               'singular': model._meta.verbose_name.lower(),
                              }, context_instance=RequestContext(request))


def registration_detail(request, slug, id):
    registrant = get_object_or_404(Registrant, slug=slug)
    registration = get_object_or_404(Registration.all_objects, id=id, registrant=registrant)

    return object_detail(request,
                         Registration.all_objects.all(),
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
        lobbyists = Lobbyist.objects.filter(display_name__icontains=term)
        positions = CoveredPosition.objects.filter(position__icontains=term)
        covered_position_lobbyists = Lobbyist.objects.none()
        for position in positions:
            covered_position_lobbyists = covered_position_lobbyists | position.lobbyist_set.all()
        covered_position_lobbyists = covered_position_lobbyists.distinct()
    else:
        registrants = None
        clients = None
        lobbyists = None
        positions = None

    num_results = registrants.count() + clients.count() + lobbyists.count() + positions.count()

    return render_to_response('willard/search.html',
                              {'registrants': registrants,
                               'clients': clients,
                               'lobbyists': lobbyists,
                               'covered_position_lobbyists': covered_position_lobbyists,
                               'term': term, 
                               'num_results': num_results,
                               },
                              context_instance=RequestContext(request))


def lobbyist_list(request):
    order_options = ('name',
                     'covered',
                     'registrants',
                     'date',
                     'registrations', )

    default_order = 'name'
    given_order = request.GET.get('order', default_order)
    if given_order.strip('-') not in order_options:
        given_order = default_order

    if given_order == 'name':
        order = ('display_name', 'name')
    elif given_order == '-name':
        order = ('-display_name', '-name')
    elif given_order == 'covered':
        order = ('denormalized_covered_positions', )
    elif given_order == '-covered':
        order = ('-denormalized_covered_positions', )
    elif given_order == 'registrants':
        order = ('denormalized_registrants', )
    elif given_order == '-registrants':
        order = ('-denormalized_registrants', )
    elif given_order == 'date':
        order = ('latest_registration_date', )
    elif given_order == '-date':
        order = ('-latest_registration_date', )
    elif given_order == 'registrations':
        order = ('registration_count', )
    elif given_order == '-registrations':
        order = ('-registration_count', )

    object_list = Lobbyist.objects.order_by(*order).select_related()
    page = make_paginator(request, object_list)

    return render_to_response('willard/lobbyist_list.html',
               {'object_list': page.object_list,
                'order': order,
                'given_order': given_order,
                'page_obj': page,
                'order': given_order.strip('-'),
                'given_order': given_order,
                'sort': 'desc' if given_order.startswith('-') else 'asc',
                },
            context_instance=RequestContext(request))

