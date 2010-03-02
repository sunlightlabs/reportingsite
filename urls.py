from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.static import serve
import settings


admin.autodiscover()


urlpatterns = patterns(
    
    'reporting.views',
    url(r'^$', 'index'),
    url(r'^admin/r/21/(?P<object_id>[0-9]+)/$', 'preview'),
    (r'^admin/', include(admin.site.urls)),
    url(r'^search/(?P<terms>.+)/$', 'search'),
    url(r'^search/$', 'searchredirect'),

    # comment urls
    url(r'^comment/', include('django.contrib.comments.urls')),
    
    # tags
    url(r'^tag/admin/$', 'tag_list_admin', name='blogdor_tag_list'),
    url(r'^tag/(?P<tag>[^/]+)/$', 'tag', name='blogdor_tag'),
    url(r'^tag/$', 'tag_list', name='blogdor_tag_list'),
    
    # archives
    url(r'^(?P<year>\d{4})/$', 'archive_year', name='blogdor_archive_year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$', 'archive_month', name='blogdor_archive_month'),
    url(r'^blog/$', 'archive', name='blogdor_archive'),
    
    # post
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$', 'post_wpcompat', name='blogdor_post_wpcompat'),  
    url(r'^(?P<year>\d{4})/(?P<slug>[\w-]+)/$', 'post', name='blogdor_post'),
    
    # author
    url(r'^author/(?P<username>[\w\s]+)/$', 'author', name='blogdor_author'),
    
    # preview
    #url(r'^preview/(?P<post_id>\d+)/(?P<slug>[\w-]+)/$', 'preview', name='blogdor_preview'),
    url(r'^features/$', 'bysite', {'site': 'features'}),
    #page by topic: flit, ss, slrg pages    
    url(r'^(?P<site>\w{1,4})/$', 'bysite'),

    url(r'^adminfiles/', include('adminfiles.urls')),

    url(r'^adminajax/(?P<user_id>\d+)/(?P<post_id>\d+)/$', 'admin_currentedit', name='admin_currentedit'),

    url(r'^recovery/', include('millions.urls')),
    url(r'^migration/', include('migration.urls')),

)




    
from reporting.feeds import *
default_feeds = {
        'latest': LatestPosts,
        'tag': LatestForTag,
        'author': LatestForAuthor,
        'features': LatestFeatures
}
    
params = {'feed_dict': default_feeds}
    
urlpatterns += patterns('django.contrib.syndication.views',
        url(r'^feeds/(?P<url>.*)/$', 'feed', params, name="blogdor_feeds"),
        url(r'^feed/atom/$', 'feed', {'feed_dict': default_feeds, 'url': 'latest'}, name="blogdor_feeds"),
        url(r'^feeds/site/(?P<site>.*)/$', 'feed', {'feed_dict': default_feeds, 'url': 'site'}, name="blogdor_feeds"),
)

from django.conf import settings
if (settings.DEBUG):  
    urlpatterns += patterns('',  
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),  
    )  


