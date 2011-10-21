from django.conf.urls.defaults import *

from hacmap.views import *

urlpatterns = patterns(
        '',


        url(r'^map\/?$',
            'django.views.generic.simple.direct_to_template',
            {'template': 'hacmap/map.html',
            },
            name='hac_map'),

        url(r'^map\/embed\/?$',
            'django.views.generic.simple.direct_to_template',
            {'template': 'hacmap/bare_map.html',
            },
            name='hac_map_bare'),

        url(r'^markers\/(?P<layer_name>[_\w]+)\/(?P<marker_id>[a-z0-9]+)\/?$',
            marker_detail,
            name='hac_marker_detail'),

        url(r'^markers\/?$',
            markers,
            name='hac_markers')

        )

