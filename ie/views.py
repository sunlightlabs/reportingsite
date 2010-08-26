from collections import defaultdict
from operator import itemgetter
import csv
import datetime
from cStringIO import StringIO

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, get_list_or_404, render_to_response
from django.views.generic import list_detail
from django.conf import settings

from ie.models import Committee

from pymongo import Connection
from pymongo.code import Code


#conn = Connection(settings.MONGODB_HOST or 'localhost', settings.MONGODB_PORT or 27017)
conn = Connection()

db = conn.independent_expenditures
filers = db.filers
contributions = db.contributions
expenditures = db.expenditures
text = db.text


def list_candidates(support_oppose=None):
    code = """
            function () {
                %s
                emit(this['crp_id'], this['EXPENDITURE AMOUNT']);
                %s
            };
            """
    if support_oppose:
        code = code % ("if (this['SUPPORT/OPPOSE CODE'] === '%s') {" % support_oppose, 
                       "}")
    else:
        code = code % ("", "")
    map = Code(code)

    reduce = Code("""
                    function (key, values) { 
                        var sum = 0;
                        for (var i in values) {
                            sum += values[i];
                        }
                        return sum;
                    };
                    """)
    result = expenditures.map_reduce(map, reduce)

    candidates = []

    for x in result.find():
        candidate = expenditures.find_one({'crp_id': x['_id']})
        candidate.update(x)
        candidates.append(candidate)

    return candidates


def list_committees():
    map = Code("""
                function () {
                    emit(this['FILER COMMITTEE ID NUMBER'], this['EXPENDITURE AMOUNT']);
                };
                """)
    reduce = Code("""
                    function (key, values) {
                        var sum = 0;
                        for (var i in values) {
                            sum += values[i];
                        }
                        return sum;
                    };
                    """)
    result = expenditures.map_reduce(map, reduce)
    committees = []
    for x in result.find():
        committee = filers.find_one({'FILER FEC ID NUMBER': x['_id']})
        committee['name'] = committee['ORGANIZATION NAME']
        committee.update(x)
        committees.append(committee)

    return committees



def index(request):
    candidates = list_candidates()
    candidates.sort(key=itemgetter('value'), reverse=True)

    committees = list_committees()
    committees.sort(key=itemgetter('value'), reverse=True)

    return render_to_response('ie/index.html',
                              {'committees': committees,
                               'candidates': candidates, }
                              )


def payee_list(request):
    map = Code("""function () {
                    emit({'slug': this['payee_slug'], 'name': this['payee_name']}, this['EXPENDITURE AMOUNT']);
                };""")
    reduce = Code("""function (key, values) {
                        var sum = 0;
                        for (var i in values) {
                            sum += values[i];
                        }
                        return sum;
                };""")
    result = expenditures.map_reduce(map, reduce)

    return render_to_response('ie/payee_list.html',
                              {'payees': [{'payee': x['_id'], 'amount': x['value']} for x in result.find().sort('_id')], }
                              )


def payee_detail(request, payee_slug):
    expends = list(expenditures.find({'payee_slug': payee_slug}))
    for expend in expends:
        committee = filers.find_one({'FILER FEC ID NUMBER': expend['FILER COMMITTEE ID NUMBER']})
        if committee:
            expend['date'] = expend['EXPENDITURE DATE']
            expend['support_oppose'] = expend['SUPPORT/OPPOSE CODE']
            expend['amount'] = expend['EXPENDITURE AMOUNT']
            expend['description'] = expend['EXPENDITURE PURPOSE DESCRIP']
            committee['name'] = committee['ORGANIZATION NAME']
            expend['committee'] = committee

    return render_to_response('ie/payee_detail.html',
                              {'expenditures': expends,
                               'payee': expends[0]['payee_name'], }
                             )

def committee_detail(request, committee_slug):
    support = committee_support_oppose(committee_slug, 'S')
    oppose = committee_support_oppose(committee_slug, 'O')
    total = support + oppose

    committee = filers.find_one({'committee_slug': committee_slug})
    committee.update({'support': support,
                      'oppose': oppose,
                      'total': total, 
                      'name': committee['ORGANIZATION NAME'],
                      })

    candidates = {'support': candidates_by_committee(committee_slug, 'S'),
                  'oppose': candidates_by_committee(committee_slug, 'O')}

    donations = list(contributions.find({'committee_slug': committee_slug}))

    return render_to_response('ie/committee_detail.html',
                              {'committee': committee,
                              'candidates': candidates,
                              'contributions': donations, }
                            )


def committee_support_oppose(committee_slug, support_oppose):
    fec_id = filers.find_one({'committee_slug': committee_slug})['FILER FEC ID NUMBER']
    map = Code("""function () {
                    if (this['SUPPORT/OPPOSE CODE'] === '%s' && this['FILER COMMITTEE ID NUMBER'] === '%s') {
                        emit(this['FILER COMMITTEE ID NUMBER'], this['EXPENDITURE AMOUNT']);
                    }
                };""" % (support_oppose, fec_id))
    reduce = Code("""function (key, values) {
                        var sum = 0;
                        for (var i in values) {
                            sum += values[i];
                        }
                        return sum;
                    };""")
    candidates = []
    result = expenditures.map_reduce(map, reduce).find_one()
    if result:
        return result['value']
    return 0


def candidates_by_committee(committee_slug, support_oppose):
    fec_id = filers.find_one({'committee_slug': committee_slug})['FILER FEC ID NUMBER']
    map = Code("""function () {
                        if (this['SUPPORT/OPPOSE CODE'] === '%s' && this['FILER COMMITTEE ID NUMBER'] === '%s') {
                            emit(this['crp_id'], this['EXPENDITURE AMOUNT']);
                        }
                    };""" % (support_oppose, fec_id))
    reduce = Code("""function (key, values) {
                        var sum = 0;
                        for (var i in values) {
                            sum += values[i];
                        }
                        return sum;
                    };""")
    candidates = []
    result = expenditures.map_reduce(map, reduce)
    for x in result.find():
        candidate = expenditures.find_one({'crp_id': x['_id']})
        candidate.update(x)
        candidates.append(candidate)

    candidates.sort(key=itemgetter('value'), reverse=True)
    return candidates


def candidate_detail(request, candidate_slug):
    support = candidate_support_oppose(candidate_slug, 'S')
    oppose = candidate_support_oppose(candidate_slug, 'O')
    total = support + oppose

    candidate = expenditures.find_one({'candidate_slug': candidate_slug})
    if not candidate:
        raise Http404

    candidate.update({'support': support,
                      'oppose': oppose,
                      'total': total, })

    committees = {'support': committees_in_support_opposition(candidate_slug, 'S'),
                  'oppose': committees_in_support_opposition(candidate_slug, 'O')}

    return render_to_response('ie/candidate_detail.html',
                              {'candidate': candidate,
                               'committees': committees, }
                              )


def committees_in_support_opposition(candidate_slug, support_oppose):
    """A list of committees that have supported/opposed the
    given candidate, and how much they've spent doing so.
    """
    map = Code("""function () {
                    if (this['SUPPORT/OPPOSE CODE'] === '%s' && this['candidate_slug'] === '%s') {
                        emit(this['FILER COMMITTEE ID NUMBER'], this['EXPENDITURE AMOUNT']);
                    }
                  };""" % (support_oppose, candidate_slug))
    reduce = Code("""function (key, values) {
                        var sum = 0;
                        for (var i in values) {
                            sum += values[i];
                        }
                        return sum;
                    };""")
    committees = []

    result = expenditures.map_reduce(map, reduce)
    for x in result.find():
        committee = filers.find_one({'FILER FEC ID NUMBER': x['_id']})
        committee['name'] = committee['ORGANIZATION NAME']
        committee.update(x)
        committees.append(committee)

    committees.sort(key=itemgetter('value'), reverse=True)
    return committees


def candidate_support_oppose(candidate_slug, support_oppose):
    map = Code("""function () {
                       if (this['SUPPORT/OPPOSE CODE'] === '%s' && this['candidate_slug'] === '%s') {
                           emit(this['CANDIDATE ID NUMBER'], this['EXPENDITURE AMOUNT']);
                       }
                  };""" % (support_oppose, candidate_slug))
    reduce = Code("""function (key, values) {
                        var sum = 0;
                        for (var i in values) {
                            sum += values[i];
                        }
                        return sum;
                      };""")
    result = expenditures.map_reduce(map, reduce)
    data = result.find_one()
    if data:
        return result.find_one()['value']

    return 0


def candidate_list(request):
    support = list_candidates('S')
    oppose = list_candidates('O')
    candidates = defaultdict(dict)
    for i in support:
        candidates[i['candidate_slug']] = {'total': i['value'], 
                                           'support': i['value'], 
                                           'oppose': 0, 
                                           'crp_name': i['crp_name'], 
                                           'candidate_slug': i['candidate_slug'], 
                                          }
    for i in oppose:
        if i['candidate_slug'] in candidates:
            candidates[i['candidate_slug']].update({'oppose': i['value'], 
                                                    'total': i['value'] + candidates[i['candidate_slug']]['support'],
                                                    })
        else:
            candidates[i['candidate_slug']] = {'total': i['value'], 
                                               'support': 0, 
                                               'oppose': i['value'], 
                                               'crp_name': i['crp_name'], 
                                               'candidate_slug': i['candidate_slug'], 
                                              }

    candidates = candidates.values()

    return render_to_response('ie/candidate_list.html',
                              {'candidates': candidates, }
                              )


def committee_list(request):
    committees = list_committees()
    committees.sort(key=itemgetter('name'))
    return render_to_response('ie/committee_list.html',
                              {'committees': committees, }
                              )


def expenditures_by_committee_for_candidate(request, candidate_slug, committee_slug):
    fec_id = filers.find_one({'committee_slug': committee_slug})['FILER FEC ID NUMBER']
    expends = expenditures.find({'candidate_slug': candidate_slug, 'FILER COMMITTEE ID NUMBER': fec_id}).sort('EXPENDITURE DATE', -1)
    clean_expends = []
    for expenditure in expends:
        expenditure['amount'] = expenditure['EXPENDITURE AMOUNT']
        expenditure['date'] = expenditure['EXPENDITURE DATE']
        expenditure['description'] = expenditure['EXPENDITURE PURPOSE DESCRIP']
        clean_expends.append(expenditure)

    clean_expends.sort(key=itemgetter('date'))

    return render_to_response('ie/expenditures_by_committee_for_candidate.html',
                              {'expenditures': clean_expends, }
                             )


def new_committees_csv(request):
    items = Committee.objects.filter(date_of_organization__gte=datetime.date(2010, 07, 01)).order_by('-date_of_organization')
    if not items:
        return Http404

    headers = [x.name for x in items[0]._meta.fields]
    data = list(reversed(list(reversed(items.values_list())) + [[x.name for x in items[0]._meta.fields]]))
    output = StringIO()
    csv.writer(output).writerows(data)
    return HttpResponse(output.getvalue(), content_type='text/plain')

