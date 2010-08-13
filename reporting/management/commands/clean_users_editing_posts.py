"""
The users editing a post are stored in a ManyToMany field. JavaScript is used 
to update the list when a user closes the story. However, it is still possible
for stale entries to end up in the database. This command is used to clear them.
"""
import datetime

from django.core.management.base import NoArgsCommand

from reporting.models import UserEditingPost


class Command(NoArgsCommand):

    help = 'Remove stale UserEditingPost entries from database.'
    requires_model_validation = False

    def handle_noargs(self, **options):
        UserEditingPost.objects.filter(timestamp__lt=datetime.datetime.now()-datetime.timedelta(minutes=1)).delete()
