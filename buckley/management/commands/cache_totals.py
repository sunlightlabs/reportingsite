import datetime
from operator import itemgetter

from django.core.management.base import BaseCommand, CommandError
from django.db.models import *

from buckley.models import *

def cache_totals():
    totals = Total.objects.all()
    if totals:
        total = totals[0]
    else:
        total = Total()
    ie_total = Expenditure.objects.filter(candidate__cycle=2010, electioneering_communication=False).aggregate(total=Sum('expenditure_amount'))['total']
    total.ie_total = ie_total
    ec_total = Expenditure.objects.filter(electioneering_communication=True).aggregate(total=Sum('expenditure_amount'))['total']
    total.ec_total = ec_total
    total.total = ie_total or 0 + ec_total or 0

    by_party = sorted(list(Expenditure.objects.exclude(support_oppose='', candidate__party='').filter(candidate__cycle=2010, candidate__party__in=['R', 'D',]).values('candidate__party', 'support_oppose').annotate(amt=Sum('expenditure_amount'))), key=itemgetter('candidate__party', 'support_oppose'), reverse=True)
    for i in by_party:
        i['party_cmtes'] = Expenditure.objects.filter(candidate__cycle=2010, committee__tax_status='FECA Party', candidate__party=i['candidate__party'], support_oppose=i['support_oppose']).aggregate(t=Sum('expenditure_amount'))['t'] or 0
        i['non_party_cmtes'] = Expenditure.objects.exclude(committee__tax_status='FECA Party').filter(candidate__cycle=2010, candidate__party=i['candidate__party'], support_oppose=i['support_oppose']).aggregate(t=Sum('expenditure_amount'))['t'] or 0

    for i in by_party:
        if i['candidate__party'] == 'R' and i['support_oppose'] == 'S':
            total.republican_support_nonparty = i['non_party_cmtes']
            total.republican_support_party = i['party_cmtes']
            total.republican_support_total = i['amt']
        elif i['candidate__party'] == 'R' and i['support_oppose'] == 'O':
            total.republican_oppose_nonparty = i['non_party_cmtes']
            total.republican_oppose_party = i['party_cmtes']
            total.republican_oppose_total = i['amt']
        elif i['candidate__party'] == 'D' and i['support_oppose'] == 'S':
            total.democrat_support_nonparty = i['non_party_cmtes']
            total.democrat_support_party = i['party_cmtes']
            total.democrat_support_total = i['amt']
        elif i['candidate__party'] == 'D' and i['support_oppose'] == 'O':
            total.democrat_oppose_nonparty = i['non_party_cmtes']
            total.democrat_oppose_party = i['party_cmtes']
            total.democrat_oppose_total = i['amt']


    cutoff = datetime.date.today() - datetime.timedelta(days=5)

    non_party_committees = Expenditure.objects.filter(candidate__cycle=2010, expenditure_date__gt=cutoff).exclude(Q(committee__slug='') | Q(committee__tax_status='FECA Party')).order_by('committee').values('committee__name', 'committee__slug').annotate(amount=Sum('expenditure_amount')).order_by('-amount')
    TopCommittee.objects.all().delete()
    for committee in non_party_committees[:10]:
        c = Committee.objects.get(slug=committee['committee__slug'])
        amount = committee['amount']
        TopCommittee.objects.create(committee=c,
                                    amount=amount)

    party_committees = Expenditure.objects.filter(candidate__cycle=2010, expenditure_date__gt=cutoff, committee__tax_status='FECA Party').exclude(committee__slug='').order_by('committee').values('committee__name', 'committee__slug').annotate(amount=Sum('expenditure_amount')).order_by('-amount')
    TopPartyCommittee.objects.all().delete()
    for committee in party_committees[:10]:
        c = Committee.objects.get(slug=committee['committee__slug'])
        amount = committee['amount']
        TopPartyCommittee.objects.create(committee=c,
                                         amount=amount)

 
    top_races = Expenditure.objects.exclude(race='', candidate=None).filter(candidate__cycle=2010, expenditure_date__gt=cutoff).order_by('race').values('race').annotate(amount=Sum('expenditure_amount')).order_by('-amount')
    TopRace.objects.all().delete()
    for race in top_races[:10]:
        TopRace.objects.create(race=race['race'],
                               amount=race['amount'])

    top_candidates = Expenditure.objects.filter(candidate__cycle=2010, expenditure_date__gt=cutoff).order_by('candidate').values('candidate').annotate(amount=Sum('expenditure_amount')).order_by('-amount')[:10]
    TopCandidate.objects.all().delete()
    for candidate in top_candidates[:10]:
        try:
            TopCandidate.objects.create(candidate=Candidate.objects.get(pk=candidate['candidate']),
                                        amount=candidate['amount'])     
        except Candidate.DoesNotExist:
            continue

    total.save()

class Command(BaseCommand):

    def handle(self, *args, **options):
        cache_totals()
