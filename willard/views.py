from collections import defaultdict
import datetime
import itertools

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db.models import *

from dateutil.relativedelta import relativedelta

from willard.models import *


def index(request):
    cutoff = datetime.date.today() - relativedelta(months=11)
    registrations = Registration.objects.filter(signed_date__lte=datetime.date.today(), signed_date__gte=cutoff)

    top_issue_ids = IssueCode.objects.filter(registration__signed_date__gte=cutoff).values_list('pk', flat=True).annotate(c=Count('registration')).order_by('-c')[:5]
    top_issues = IssueCode.objects.filter(pk__in=list(top_issue_ids))
    months = []
    curr = cutoff
    issue_counts = defaultdict(list)
    while curr <= datetime.date.today():
        months.append(curr.strftime('%b')[0])
        for issue in top_issues:
            issue_counts[issue.issue].append(issue.registration_set.filter(signed_date__month=curr.month, signed_date__year=curr.year).count())
        curr += relativedelta(months=1)

    return render_to_response('willard/index.html',
                              {'object_list': registrations.filter(signed_date__gte=datetime.date.today()-relativedelta(months=1)),
                               'issue_counts': issue_counts.items(),
                               'months': months,
                               'issues': IssueCode.objects.exclude(issue='').order_by('issue'),
                                },
                              context_instance=RequestContext(request))


def issue_detail(request, code):
    issue_code = get_object_or_404(IssueCode, code=code)
    registrations = issue_code.registration_set.all()

    min_date = Registration.objects.order_by('signed_date').values_list('signed_date', flat=True)[0]
    max_date = datetime.date.today()

    year_groups = itertools.groupby(registrations, key=lambda x: x.signed_date.year)
    date_data = []
    for year, regs in year_groups:
        month_groups = itertools.groupby(regs, key=lambda x: x.signed_date.month)
        for month, month_registrations in month_groups:
            date = datetime.date(2010, month, 1)
            date_data.append((date, list(month_registrations)))

    # Get month counts for the past 12 months.
    month_counts = []
    curr = datetime.date.today()
    while len(month_counts) < 12:
        month_counts.append({'month': curr.month, 'year': curr.year, 'count': registrations.filter(signed_date__year=curr.year, signed_date__month=curr.month).count()})
        curr -= relativedelta(months=1)
    month_counts.reverse()
    

    return render_to_response('willard/issuecode_detail.html',
                              {
                               'issue_code': issue_code,
                               'date_data': date_data,
                               'month_counts': month_counts,
                               #'registrations': registrations, 
                               #'dates': dates,
                               },
                              context_instance=RequestContext(request))

