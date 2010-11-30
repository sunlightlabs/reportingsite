import datetime

from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404

from willard.models import *

def make_item_description(item):
    description = """%s registered on %s to lobby for %s. The issues listed are %s. The specific issue listed is "%s" """ % (item.organization.name,
            item.signed_date.strftime("%F %j, %Y"),
            item.client.name,
            ', '.join([x.issue for x in item.issues.all()]),
            item.specific_issues, )
    return description


class RegistrationFeed(Feed):
    title = 'Latest lobbyist registrations'
    link = '/lobbying/rss'
    description = 'The latest lobbyist registrations submitted to the House of Representatives'

    def items(self):
        return Registration.objects.order_by('-signed_date')[:50]

    def item_link(self, item):
        return '/lobbying'

    def item_description(self, item):
        return make_item_description(item)

    def item_pubdate(self, item):
        date = item.signed_date
        return datetime.datetime(date.year, date.month, date.day)

    def item_title(self, item):
        return '%s registered to lobby for %s' % (item.organization.name,
                                                  item.client.name)

class IssueFeed(Feed):

    def get_object(self, request, code):
        return get_object_or_404(IssueCode, code=code)

    def title(self, obj):
        return 'Lobbyist registrations: %s' % obj.issue

    def link(self, obj):
        return obj.get_absolute_url()

    def item_description(self, item):
        return make_item_description(item)

    def items(self, obj):
        return obj.registration_set.order_by('-signed_date')[:50]

    def item_title(self, item):
        return '%s registered to lobby for %s' % (item.organization.name,
                                                  item.client.name)

    def item_pubdate(self, item):
        date = item.signed_date
        return datetime.datetime(date.year, date.month, date.day)

    def item_link(self, item):
        return '/lobbying'
