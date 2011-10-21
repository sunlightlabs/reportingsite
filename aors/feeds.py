import datetime

from aors.models import *

from django.contrib.syndication.views import Feed


class AORFeed(Feed):
    title = 'Latest Advisory Opinion Request documents'
    link = '/aors/rss'
    description = 'The latest Advisory Opinion Requests and comments submitted to the FEC (via http://saos.nictusa.com/saos/searchao?SUBMIT=pending)'

    def items(self):
        return AORDocument.objects.all()

    def item_title(self, item):
        return '%s: %s' % (item.aor_number,
                           item.doc_description)

    def item_description(self, item):
        return '%s was submitted to the FEC related to %s, %s (%s)' % (item.doc_description,
                                                                       item.aor_number,
                                                                       item.org,
                                                                       item.aor_description, )

    def item_pubdate(self, item):
        return item.timestamp

    def item_link(self, item):
        return item.doc_url
