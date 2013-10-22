import csv
import sys

from django.core.management.base import BaseCommand

from reporting.models import Post


class Command(BaseCommand):
    help = 'Generate a mapping between post URLs and migrated URLs'

    def handle(self, *args, **options):

        posts = Post.objects.published()

        writer = csv.writer(sys.stdout)

        for post in posts:

            pre_url = "http://reporting.sunlightfoundation.com%s" % post.get_absolute_url()
            post_url = "http://sunlightfoundation.com/blog/%s/%s" % (post.date_published.stftime("%Y/%m/%d"), post.slug.rstrip('-'))

            writer.writerow((pre_url, post_url))
