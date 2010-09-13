import datetime

from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404

from buckley.models import *


def make_expenditure_description(item):
    return '%s spent $%s on %s %s %s' % (item.committee,
                                         intcomma(item.expenditure_amount),
                                         item.expenditure_purpose,
                                         'in support of' if item.support_oppose == 'S' else 'in opposition to',
                                         item.candidate)

class ExpenditureFeed(Feed):
    title = "Newest independent expenditure"
    link = "/rss/"
    description = "The latest independent expenditures"

    def items(self):
        return Expenditure.objects.all()[:15]

    def item_link(self, item):
        return item.get_absolute_url()

    def item_description(self, item):
        return make_expenditure_description(item)

    def item_pubdate(self, item):
        return datetime.datetime.combine(item.expenditure_date, datetime.time())


class CandidateFeed(Feed):

    def get_object(self, request, slug):
        return get_object_or_404(Candidate, slug=slug)

    def title(self, obj):
        return obj.fec_name

    def link(self, obj):
        return obj.get_absolute_url()

    def item_description(self, item):
        return make_expenditure_description(item)

    def items(self, obj):
        return Expenditure.objects.filter(candidate=obj)[:15]


class CommitteeFeed(Feed):

    def get_object(self, request, slug):
        return get_object_or_404(Committee, slug=slug)

    def title(self, obj):
        return obj.name

    def link(self, obj):
        return obj.get_absolute_url()

    def item_description(self, item):
        return make_expenditure_description(item)

    def items(self, obj):
        return Expenditure.objects.filter(committee=obj)[:15]


class PayeeFeed(Feed):

    def get_object(self, request, slug):
        return get_object_or_404(Payee, slug=slug)

    def title(self, obj):
        return obj.name

    def link(self, obj):
        return obj.get_absolute_url()

    def item_description(self, item):
        return make_expenditure_description(item)

    def items(self, obj):
        return Expenditure.objects.filter(payee=obj)[:15]

