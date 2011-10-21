from django.conf.urls.defaults import *

from aors.feeds import *


urlpatterns = patterns('',

        url(r'^rss',
            AORFeed(),
            name='aors_doc_feed')

        )
