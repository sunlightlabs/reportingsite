# Django settings for reportingsite project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

MANAGERS = ADMINS

CACHE_BACKEND = 'memcached://127.0.0.1:11211'


DATABASES = {
        'default': {
            'NAME': '',
            'USER': '',
            'PASSWORD': '',
            'ENGINE': 'django.db.backends.mysql',
            #'HOST': 'belushi.sunlightlabs.org',
	    'HOST': '',
            'PORT': '',
            }
        }


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
#MEDIA_URL = '/media/'
MEDIA_URL = '//assets-reporting.s3.amazonaws.com/1.0/'
#MEDIA_URL = 'http://reporting.sunlightlabs.com/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'http://assets.sunlightfoundation.com.s3.amazonaws.com/admin/1.2.1/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'middleware.JSONPmiddleware.JSONPMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'gatekeeper.middleware.GatekeeperMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',

)

ROOT_URLCONF = 'reportingsite.urls'

TEMPLATE_DIRS = (
    #'reportingsite/templates'
    '/projects/reporting/src/reportingsite/templates'
)

INSTALLED_APPS = (
    'django.contrib.comments',
    'django.contrib.markup',
    'tagging',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'feedinator',
    #'feedparser', # Feedparser is a single python file, not a module. This isn't allowed as of http://code.djangoproject.com/changeset/12950
    'reporting',
    'django.contrib.humanize',
    'mediasync',
    #'reportingsite.millions',
    'storages',
    'debug_toolbar',
    'haystack',
    'south',
    'buckley',
    'gunicorn',
    'willard',
    'hacmap',
    'aors',
    'findatcat',
    #'valeo',
    'doddfrank',
#    'rebuckley',
    'outside_spending',
    'outside_spending_2014',
    'fec_alerts',
    'django.contrib.redirects',
)

INTERNAL_IPS = ('127.0.0.1','localhost')

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}


DEFAULT_MARKUP = 'plain'
BLOGDOR_POSTS_PER_PAGE = 14
BLOGDOR_ENABLE_FEEDS = True

AKISMET_KEY = ''

WHICHSITE_CHOICES = [('SLRG', 'Sunlight Reporting Group'), ('SS', 'SubsidyScope'), ('FLIT', 'FLIT')]
ENTRY_TYPES = [('B', 'Blog'), ('R','Report')]

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "context_processors.latest_by_site",
    "context_processors.outside_spending_updated",
    "django.core.context_processors.request",
#    "outside_spending_2014.cycle_context_processor.add_cycle",
)

MEDIASYNC_AWS_KEY = ""
MEDIASYNC_AWS_SECRET = ""
MEDIASYNC_AWS_BUCKET = "" #"bucket_name"
MEDIASYNC_AWS_PREFIX = ""
MEDIASYNC_SERVE_REMOTE = True

MEDIASYNC = {
    'BACKEND': 'mediasync.backends.s3',
    'AWS_KEY': MEDIASYNC_AWS_KEY,
    'AWS_SECRET': MEDIASYNC_AWS_SECRET,
    'AWS_BUCKET': MEDIASYNC_AWS_BUCKET,
    'AWS_PREFIX': MEDIASYNC_AWS_PREFIX,
    'SERVE_REMOTE': MEDIASYNC_SERVE_REMOTE,
}

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID  = MEDIASYNC_AWS_KEY
AWS_SECRET_ACCESS_KEY = MEDIASYNC_AWS_SECRET
AWS_STORAGE_BUCKET_NAME = MEDIASYNC_AWS_BUCKET

"""
HAYSTACK_SEARCH_ENGINE = 'solr'
#HAYSTACK_SOLR_URL = ''
HAYSTACK_SOLR_URL = ''

HAYSTACK_SITECONF = 'search_sites'

"""
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 20

try:
    from local_settings import *
except ImportError, exp:
    pass
