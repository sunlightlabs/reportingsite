from collections import defaultdict
import datetime
from operator import itemgetter
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.template import loader, Context

from doddfrank.views import _collection


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
            make_option('--html',
                        action='store_true',
                        dest='html',
                        default=False,
                        help='Output as HTML'),
            make_option('--orgs',
                        action='store',
                        dest='orgs',
                        help='Organizations to create timelines for.'),
        )

    def handle(self, *args, **options):
        orgs = options.get('orgs', '').split(',')
        collection = _collection()

        agencies = collection.distinct(key='agency')

        start = datetime.datetime(2011, 1, 1, 0, 0, 0)
        end = datetime.datetime(2011, 6, 30, 0, 0, 0)

        days = self._weekdays(start, end)
        timelines = []

        template = loader.get_template('doddfrank/timeline.html')

        for org in orgs:

            timeline = collection.find({'organizations': org,
                                        'meeting_time': {'$gte': start,
                                                         '$lte': end, }
                                       },
                                       fields=['meeting_time', 'agency', ]
                                       )

            timeline_dict = defaultdict(list)
            for result in timeline:
                timeline_dict[result['meeting_time'].date()].append(result['agency'])

            all_days = []
            for day in days:
                td = timeline_dict.get(day, [])
                if len(td) > 1:
                    all_days.append((day, 'multiple'))
                elif len(td) == 1:
                    all_days.append((day, td[0]))
                else:
                    all_days.append((day, None))

            timelines.append({'org': org,
                              'timeline': all_days, })

        context = Context({'timelines': timelines, })
        print template.render(context)


    def _all_dates(self, start, end):
        dates = []
        while start <= end:
            dates.append(start.date())
            start += datetime.timedelta(1)
        return dates

    def _weekdays(self, start, end):
        return [x for x in self._all_dates(start, end) if x.weekday() < 5]

