import codecs
import datetime
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from reporting.models import Post
#import blogdor

EXPORT_PATH = './export/'
PER_PAGE = 200


class Command(BaseCommand):
    help = 'Export published posts in WXR format'

    def handle(self, *args, **options):

        offset = 0
        limit = PER_PAGE
        page = 0

        while 1:

            page += 1

            posts = Post.objects.published().filter(show_on_index_pages=True)[offset:limit]

            if posts.count() == 0:
                break

            author_ids = set(posts.values_list('author', flat=True))

            context = {
                'now': datetime.datetime.utcnow(),
                'generator': 'reportingsite/wpexport',
#                'generator': 'django-blogdor-%s/wpexport' % blogdor.__version__,
                'authors': User.objects.filter(pk__in=author_ids),
                'posts': posts,
            }

            content = render_to_string('export.wxr', context)

            path = os.path.join(EXPORT_PATH, 'blogdor-%03i.wxr' % page)

            print path

            with codecs.open(path, 'w', 'utf-8') as outfile:
                outfile.write(content)

            offset = limit
            limit += PER_PAGE
