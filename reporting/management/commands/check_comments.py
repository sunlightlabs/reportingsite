"""
Check old comments for spam.
"""
import datetime

from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.core.management.base import NoArgsCommand

from reporting.models import Post

from akismet import Akismet


AKISMET_KEY = getattr(settings, "AKISMET_KEY", None)


class Command(NoArgsCommand):

    help = 'Checks old comments for spam.'
    requires_model_validation = False

    def handle_noargs(self, **options):

        comments = Comment.objects.filter(is_public=True, is_removed=False, submit_date__gte=datetime.date(2010, 07, 01))
        for comment in comments:
            a = Akismet(AKISMET_KEY, blog_url='http://%s/' % Site.objects.get_current().domain)

            akismet_data = {
                'user_ip': comment.ip_address,
                'user_agent': 'Mozilla/5.0 (X11; U; Linux x86_64; de; rv:1.9.2.8) Gecko/20100723 Ubuntu/10.04 (lucid) Firefox/3.6.8',
                'comment_author': comment.user_name.encode('ascii','ignore'),
                'comment_author_email': comment.user_email.encode('ascii','ignore'),
                'comment_author_url': comment.user_url.encode('ascii','ignore'),
                'comment_type': 'comment',
            }

            is_spam = a.comment_check(comment.comment.encode('ascii', 'ignore'), akismet_data)

            if is_spam:
                post = Post.objects.get(pk=comment.object_pk)
                #print comment.user_name.encode('ascii', 'ignore'), post.get_absolute_url() + '#' + str(comment.pk)
                comment.is_removed = True
                comment.is_public = False
                comment.save()
