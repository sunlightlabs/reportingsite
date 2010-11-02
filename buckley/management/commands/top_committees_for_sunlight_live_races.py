
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.management.base import BaseCommand, CommandError
from django.db.models import *

from buckley.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        races = ['PA-Senate',
                'WV-Senate',
                'MD-1',
                'PA-11',
                'VA-5',
                'IL-Senate',
                'MO-Senate',
                'MI-7',
                'OH-16',
                'CO-Senate',
                'NV-Senate',
                'AZ-5',
                'NV-3',
                'WA-Senate',
                'CA-Senate',
                'WA-3',]

        for race in races:
            committees = Expenditure.objects.filter(race=race) \
                    .order_by('committee__name') \
                    .values('committee__name') \
                    .annotate(t=Sum('expenditure_amount')) \
                    .order_by('-t')[:5]

            print '%s: %s' % (race,
                              '; '.join(['%s ($%s)' % (x['committee__name'], intcomma(x['t'])) for x in committees]))
            print
