from django.core import urlresolvers
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.comments.moderation import CommentModerator, moderator
from django.contrib.sites.models import Site

from akismet import Akismet


AKISMET_KEY = getattr(settings, "AKISMET_KEY", None)


class BlogdorModerator(CommentModerator):
    email_notification = False
    enable_field = 'comments_enabled'

    def email(self, comment, content_object, request):

        from_email = "bounce@%s" % Site.objects.get_current().domain

        subject = "Comment on %s pending your approval" % content_object.title
        appr_link = 'http://%s%s' % (Site.objects.get_current().domain, urlresolvers.reverse('comments-approve', args=(comment.id,))   )
        message = '\n\n'.join((comment.get_as_text(), appr_link))
        recipient_email = content_object.author.email

        send_mail(subject, message, from_email, (recipient_email,), fail_silently=False)


    def moderate(self, comment, content_object, request):
        a = Akismet(AKISMET_KEY, blog_url='http://%s/' % Site.objects.get_current().domain)

        akismet_data = {
            'user_ip': comment.ip_address,
            'user_agent': request.META['HTTP_USER_AGENT'],
            'comment_author': comment.user_name.encode('ascii','ignore'),
            'comment_author_email': comment.user_email.encode('ascii','ignore'),
            'comment_author_url': comment.user_url.encode('ascii','ignore'),
            'comment_type': 'comment',
        }

        is_spam = a.comment_check(comment.comment.encode('ascii','ignore'), akismet_data)

        comment.is_public = False
        comment.save()

        if not is_spam:
           self.email(comment, content_object, request)

        return True
