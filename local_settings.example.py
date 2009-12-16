import os
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'reporting.sql'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)
