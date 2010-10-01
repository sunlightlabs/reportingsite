import datetime

from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404

from buckley.models import *


def make_expenditure_description(item):
    if not item.electioneering_communication:
        return '%s spent $%s on %s %s %s' % (item.committee,
                                             intcomma(item.expenditure_amount),
                                             item.expenditure_purpose,
                                             'in support of' if item.support_oppose == 'S' else 'in opposition to',
                                             item.candidate)
    else:
        return '%s spent %s on an electioneering communication mentioning %s' % (item.committee,
                intcomma(item.expenditure_amount),
                ', '.join([x.__unicode__() for x in item.electioneering_candidates.all()]))

class ExpenditureFeed(Feed):
    title = "Latest outside spending"
    link = "/rss/"
    description = "The latest outside spending in congressional elections"

    def items(self):
        return Expenditure.objects.all()[:50]

    def item_link(self, item):
        return item.get_absolute_url()

    def item_description(self, item):
        return make_expenditure_description(item)

    def item_pubdate(self, item):
        return datetime.datetime.combine(item.expenditure_date, datetime.time())

    def item_title(self, item):
        if item.electioneering_communication:
            return '%s: %s' % (item.committee,
                                ', '.join([x.__unicode__() for x in item.electioneering_candidates.all()]))
        else:
            return '%s: %s' % (item.committee, item.candidate)

    def item_pubdate(self, item):
        return item.timestamp


class CandidateFeed(Feed):

    def get_object(self, request, slug):
        return get_object_or_404(Candidate, slug=slug)

    def title(self, obj):
        return 'Outside spending: %s' % obj

    def link(self, obj):
        return obj.get_absolute_url()

    def item_description(self, item):
        return make_expenditure_description(item)

    def items(self, obj):
        all = obj.expenditure_set.all() | obj.electioneering_expenditures.all()
        return all.order_by('-expenditure_date')[:50]

    def item_title(self, item):
        return '%s: $%s' % (item.committee, intcomma(item.expenditure_amount))

    def item_link(self, item):
        return item.get_absolute_url() + '#' + str(item.pk)

    def item_pubdate(self, item):
        return item.timestamp


class CommitteeFeed(Feed):

    def get_object(self, request, slug):
        return get_object_or_404(Committee, slug=slug)

    def title(self, obj):
        return 'Outside spending: %s' % obj.name

    def link(self, obj):
        return obj.get_absolute_url()

    def item_description(self, item):
        return make_expenditure_description(item)

    def items(self, obj):
        return Expenditure.objects.filter(committee=obj)[:15]

    def item_title(self, item):
        if item.electioneering_communication:
            return ', '.join([x.__unicode__() for x in item.electioneering_candidates.all()])
        else:
            return item.candidate

    def item_link(self, item):
        return item.get_absolute_url() + '#' + str(item.pk)

    def item_pubdate(self, item):
        return item.timestamp


class CommitteeLetterFeed(Feed):

    title = 'Committees raising unlimited amounts'
    link = '/independent-expenditures/letters/rss'
    description = 'A feed of committees that have file letters with the FEC stating their intent to raise unlimited amounts'

    def items(self):
        return IEOnlyCommittee.objects.all()[:25]

    def item_link(self, item):
        return item.get_absolute_url()

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        monthday = item.date_letter_submitted.strftime('%d').lstrip('0')
        date = item.date_letter_submitted.strftime('%A, %B %%s, %Y') % monthday
        return '%s filed a letter with the FEC on %s stating its intent to raise unlimited amounts for independent expenditures' % (item.name,
               date)

    def item_pubdate(self, item):
        return datetime.datetime.combine(item.date_letter_submitted, datetime.time())


class RaceFeed(Feed):

    def link(self, obj):
        return '/independent-expenditures/race/%s' % self.race

    def get_object(self, request, race):
        self.race = race

    def title(self, obj):
        expenditure = Expenditure.objects.filter(race=self.race, electioneering_communication=False)[0]
        return 'Outside spending: %s' % expenditure.candidate.full_race_name()

    def item_link(self, item):
        return item.get_absolute_url() + '#' + str(item.pk)

    def items(self):
        return Expenditure.objects.filter(race=self.race)

    def item_title(self, item):
        if item.electioneering_communication:
            return '%s: %s' % (item.committee,
                                ', '.join([x.__unicode__() for x in item.electioneering_candidates.all()]))
        else:
            return '%s: %s' % (item.committee, item.candidate)

    def item_description(self, item):
        return make_expenditure_description(item)

    def item_pubdate(self, item):
        return item.timestamp
