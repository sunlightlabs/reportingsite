import datetime

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
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
    description = 'The latest lobbyist registrations submitted to the U.S. Senate'

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


class GenericLobbyingFeed(Feed):
    def get_object(self, request, slug, model):
        return get_object_or_404(model, slug=slug)

    def title(self, obj):
        return 'Lobbyist registrations: %s' % obj

    def item_description(self, item):
        return make_item_description(item)

    def items(self, obj):
        return obj.registration_set.order_by('-received')[:50]

    def item_title(self, item):
        return '%s registered to lobby for %s' % (item.registrant,
                                                  item.client)

    def item_pubdate(self, item):
        return item.received

    def link(self, obj):
        return obj.get_absolute_url()


class PostEmploymentFeed(Feed):
    title = 'Upcoming lobbying restriction expirations'
    link = '/lobbying/postemployment.rss'
    description = 'Upcoming expirations of lobbying restrictions for Senate and House members and staffers'

    def items(self):
        cutoff = datetime.date.today() + datetime.timedelta(7)
        return PostEmploymentNotice.objects.filter(end_date__gte=datetime.date.today(), end_date__lte=cutoff)

    def item_link(self, item):
        return item.get_absolute_url()

    def item_description(self, item):
        return '%s left the office "%s" in the %s on %s. The lobbying restriction ends on %s' % (
                                    str(item),
                                    item.office_name,
                                    item.body,
                                    item.begin_date.strftime('%m/%d/%Y'),
                                    item.end_date.strftime('%m/%d/%Y')
                                )

    def item_pubdate(self, item):
        date = item.end_date - datetime.timedelta(7)
        return datetime.datetime(date.year, date.month, date.day)

    def item_title(self, item):
        return 'Lobbying restriction on %s ends %s' % (str(item),
                                                       item.end_date.strftime('%m/%d/%Y'))
