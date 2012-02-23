import re

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.static import serve

from reporting.feeds import *

admin.autodiscover()

def buckley_redirect(request, *args, **kwargs):
    return HttpResponsePermanentRedirect(
        re.sub(r'independent-expenditures', 'outside-spending', request.path))

urlpatterns = patterns('reporting.views',

    url(r'^$', 'index'),
    url(r'^adminfiles/', 'adminfiles'),
    url(r'^editing/', 'admin_editing', name='admin_editing'),
    url(r'^independent-expenditures/.*', buckley_redirect),
    url(r'^search/', 'search', name='reporting_search'),

    # mounted apps
    url(r'^admin/', include(admin.site.urls)),
    url(r'^aors/', include('aors.urls')),
    url(r'^buriedtreasure/', include('findatcat.urls')),
    url(r'^doddfrank/', include('doddfrank.urls')),
    url(r'^hac/', include('hacmap.urls')),
    url(r'^lobbying/', include('willard.urls')),
    url(r'^outside-spending/', include('buckley.urls')),
    url(r'^outside-spending/$', redirect_to, {'url': '/super-pacs/all/'}, name='buckley_index'),
    url(r'^recovery/', include('millions.urls')),
    # super pac hack:
    url(r'^super-pacs/', include('rebuckley.urls')),

    # comment urls
    url(r'^comment/', include('django.contrib.comments.urls')),
    
    # tags
    url(r'^tag/admin/$', 'tag_list_admin', name='blogdor_tag_list'),
    url(r'^tag/(?P<tag>[^/]+)/$', 'tag', name='blogdor_tag'),
    url(r'^tag/$', 'tag_list', name='blogdor_tag_list'),

    # documents
    url(r'^docs/', direct_to_template,
        {'template': 'dc.html'}, name='reporting_document'),
    url(r'^mortgage-fraud\/?$', direct_to_template,
        {'template': 'fincen/index.html'}, name='reporting_fincen'),
    url(r'^fincen\.html\/?$', direct_to_template,
        {'template': 'fincen/fincen.html'}, name='reporting_fincen'),
    url(r'^fincen\.js\/?$', direct_to_template,
        {'template': 'fincen/fincen.js', 'mimetype': 'text/javascript'}, name='reporting_fincen_js'),
    
    # blog posts
    url(r'^(?P<year>\d{4})/$',
        'archive_year', name='blogdor_archive_year'),
    url(r'^(?P<year>\d{4})/(?P<slug>[\w-]+)/$',
        'post_detail', name='blogdor_post'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        'archive_month', name='blogdor_archive_month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$',
        'post_detail', name='blogdor_post_wpcompat'),
    url(r'^author/(?P<username>[\w\s]+)/$', 'author', name='blogdor_author'),
    url(r'^blog/$', 'archive', name='blogdor_archive'),
    url(r'^features/$', 'bysite', {'site': 'features'}),
    url(r'^(?P<site>\w{1,4})/$', 'bysite'),
    #url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$', 'post_wpcompat', name='blogdor_post_wpcompat'),

    # budget forecasts vs reality
    url(r'^budgets/', direct_to_template, {'template': 'budgetforecasts/budgets.html'}),
)

#
# RSS feeds
#

default_feeds = {
    'latest': LatestPosts,
    'tag': LatestForTag,
    'author': LatestForAuthor,
    'features': LatestFeatures
}

urlpatterns += patterns('django.contrib.syndication.views',
    url(r'^feeds/(?P<url>.*)/$', 'feed',
        {'feed_dict': default_feeds}, name="blogdor_feeds"),
    url(r'^feed/atom/$', 'feed',
        {'feed_dict': default_feeds, 'url': 'latest'}, name="blogdor_feeds"),
    url(r'^feeds/site/(?P<site>.*)/$', 'feed',
        {'feed_dict': default_feeds, 'url': 'site'}, name="blogdor_feeds"),
)

#
# mediasync debug pattern
#

if (settings.DEBUG):  
    urlpatterns += patterns('',  
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),  
    )

