import datetime

from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404

from willard.models import *

def make_item_description(item):
    description = """%s registered on %s to lobby for %s. The issues listed are %s. The specific issue listed is "%s" """ % (item.registrant,
            item.received.strftime("%F %j, %Y"),
            item.client,
            ', '.join([x.issue for x in item.denormalized_issues]),
            item.specific_issue, )
    return description


class RegistrationFeed(Feed):
    title = 'Latest lobbyist registrations'
    link = '/lobbying/rss'
    description = 'The latest lobbyist registrations submitted to the House of Representatives'

    def items(self):
        return Registration.objects.order_by('-received')[:50]

    def item_link(self, item):
        return '/lobbying'

    def item_description(self, item):
        return make_item_description(item)

    def item_pubdate(self, item):
        date = item.received
        return datetime.datetime(date.year, date.month, date.day)

    def item_title(self, item):
        return '%s registered to lobby for %s' % (item.registrant,
                                                  item.client)

class IssueFeed(Feed):

    def get_object(self, request, slug):
        return get_object_or_404(Issue, slug=slug)

    def title(self, obj):
        return 'Lobbyist registrations: %s' % obj.issue

    def link(self, obj):
        return obj.get_absolute_url()

    def item_description(self, item):
        return make_item_description(item)

    def items(self, obj):
        return obj.registration_set.order_by('-received')[:50]

    def item_title(self, item):
        return '%s registered to lobby for %s' % (item.registrant,
                                                  item.client)

    def item_pubdate(self, item):
        return item.received


class RegistrantFeed(Feed):

    def get_object(self, request, slug):
        return get_object_or_404(Registrant, slug=slug)

    def title(self, obj):
        return 'Lobbyist registrations by %s' % obj

    def item_description(self, item):
        return make_item_description(item)

    def items(self, obj):
        return obj.registration_set.order_by('-received')[:50]

    def item_titele(self, item):
        return '%s registered to lobby for %s' % (item.registrant,
                                                  item.client)

    def item_pubdate(self, item):
        return item.received

    def link(self, obj):
        return obj.get_absolute_url()


class ClientFeed(Feed):

    def get_object(self, request, slug):
        return get_object_or_404(Client, slug=slug)

    def title(self, obj):
        return 'Lobbyist registrations for %s' % obj

    def item_description(self, item):
        return make_item_description(item)

    def items(self, obj):
        return obj.registration_set.order_by('-received')[:50]

    def item_titele(self, item):
        return '%s registered to lobby for %s' % (item.registrant,
                                                  item.client)

    def item_pubdate(self, item):
        return item.received

    def link(self, obj):
        return obj.get_absolute_url()
