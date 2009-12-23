# Django settings for reportingsite project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Luke', 'lrosiak@sunlightfoundation.com'),
)


MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'reporting.sql'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

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
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'http://assets.sunlightfoundation.com.s3.amazonaws.com/admin/1.1.1/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '***REMOVED***'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'gatekeeper.middleware.GatekeeperMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware'
)

ROOT_URLCONF = 'reportingsite.urls'

TEMPLATE_DIRS = (
    'reportingsite/templates'
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
    'feedparser',
    'reporting',
    'django.contrib.humanize',
    'adminfiles',
    'sorl.thumbnail',
    'mediasync',
    'markdown'
)


DEFAULT_MARKUP = 'plain'
BLOGDOR_POSTS_PER_PAGE = 14
BLOGDOR_ENABLE_FEEDS = True

AKISMET_KEY = '***REMOVED***'

WHICHSITE_CHOICES = [('SLRG', 'Sunlight Reporting Group'), ('SS', 'SubsidyScope'), ('FLIT', 'FLIT')]
ENTRY_TYPES = [('B', 'Blog'), ('R','Report')]

MEDIASYNC_AWS_KEY = "***REMOVED***"
MEDIASYNC_AWS_SECRET = "***REMOVED***"
MEDIASYNC_AWS_BUCKET = "assets.sunlightfoundation.com" #"bucket_name"  
MEDIASYNC_AWS_PREFIX = "reporting/1.0"

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "context_processors.latest_by_site",
)

ADMINFILES_MEDIA_URL = 'http://assets.sunlightfoundation.com.s3.amazonaws.com/reporting/1.0/admin/'
ADMINFILES_USE_SIGNALS = True
ADMINFILES_REF_START = '[{['
ADMINFILES_REF_END = ']}]'
FLICKR_USER = None
YOUTUBE_USER = None


try:
    from local_settings import *
except ImportError, exp:
    pass
