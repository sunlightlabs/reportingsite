from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.static import serve

import settings


admin.autodiscover()



urlpatterns = patterns(
    'reporting.views',
    url(r'^$', 'index'),
    (r'^admin/', include(admin.site.urls)),

    url(r'^dashboard$', 'feedbar'),

    url(r'^search/$', 'search'),

    # comment urls
    url(r'^comment/', include('django.contrib.comments.urls')),
    
    # tags
    url(r'^tag/admin/$', 'tag_list_admin', name='blogdor_tag_list'),
    url(r'^tag/(?P<tag>[^/]+)/$', 'tag', name='blogdor_tag'),
    url(r'^tag/$', 'tag_list', name='blogdor_tag_list'),
    
    # archives
    url(r'^(?P<year>\d{4})/$', 'archive_year', name='blogdor_archive_year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$', 'archive_month', name='blogdor_archive_month'),
    url(r'^archive/$', 'archive', name='blogdor_archive'),
    
    # post
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$', 'post_wpcompat', name='blogdor_post_wpcompat'),  
    url(r'^(?P<year>\d{4})/(?P<slug>[\w-]+)/$', 'post', name='blogdor_post'),
    
    # author
    url(r'^author/(?P<username>[\w]+)/$', 'author', name='blogdor_author'),
    
    # preview
    url(r'^preview/(?P<post_id>\d+)/(?P<slug>[\w-]+)/$', 'preview', name='blogdor_preview'),

    #pages by length (blog or report)
    url(r'^realtime$', 'realtime'),
    url(r'^stories$', 'stories'),
    #page by topic: flit, ss, slrg pages    
    url(r'^(?P<site>.\w{1,5})/$', 'bysite'),
)




    
from reporting.feeds import (LatestPosts, LatestComments, LatestForAuthor, LatestForTag)
    
default_feeds = {
        'latest': LatestPosts,
        'comments': LatestComments,
        'tag': LatestForTag,
        'author': LatestForAuthor,
}
    
params = {'feed_dict': default_feeds}
    
urlpatterns += patterns('django.contrib.syndication.views',
        url(r'^feeds/(?P<url>.*)/$', 'feed', params, name="blogdor_feeds"),
)


urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/luke/reportingsite/reporting/media/' }),
)
