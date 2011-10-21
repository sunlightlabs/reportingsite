from django.core.management.base import BaseCommand, CommandError
from django.db.models import *

from buckley.models import *

class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        for committee in Committee.objects.all():
    c = defaultdict(list)
    x = committee.expenditure_set.order_by('candidate').values('candidate__slug', 'support_oppose').annotate(Count('support_oppose'))
    for i in x:
        c[i['candidate__slug']].append(i)
    print [(k, v) for k, v in c.iteritems() if len(v) > 1]
        """
        for committee in Committee.objects.all():
            c = defaultdict(list)
            x = committee.expenditure_set.filter(electioneering_communication=False, support_oppose__in=('S', 'O')).order_by('candidate').values('candidate__slug', 'committee__slug', 'support_oppose').annotate(Count('support_oppose'))
            for i in x:
                c[i['candidate__slug']].append(i)
            d = [(k, v) for k, v in c.iteritems() if len(v) > 1]
            if d:
                print
                print committee
                for j in d:
                    print j
