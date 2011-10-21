from optparse import make_option
import datetime
import math

from dateutil.parser import parse as dateparse

from django.core.management.base import BaseCommand, CommandError
from django.db.models import *

from buckley.models import *

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
            make_option('--start',
                action='store',
                dest='start',
                default='2010-10-01',
                help='Start date for calculating trends.'),
            make_option('--end',
                action='store',
                dest='end',
                default='2010-10-01',
                help='End date for calculating trends.'),
            make_option('--model',
                action='store',
                dest='model',
                default='Committee',
                help='Model to calculate trends for.'),
            make_option('--size',
                action='store',
                dest='size',
                default='3',
                help='Size in days to use for trend calculation.'),
            )


    def handle(self, *args, **options):

        start = dateparse(options.get('start')).date()
        end = dateparse(options.get('end')).date()
        try:
            size = int(options.get('size'))
        except ValueError:
            raise CommandError('size argument must be an integer.')

        valid_models = ['Committee', 'Candidate', 'Race', ]
        model = options.get('model')
        if model not in valid_models:
            raise CommandError('%s is not a valid model' % model)

        self.model_trend(model, start, end, size)


    def model_trend(self, model, start, end, size=3):
        func = {'Committee': self.committee_trend_for_datesets,
                'Candidate': self.candidate_trend_for_datesets,
                'Race': self.race_trend_for_datesets,
                }[model]

        datesets = []
        for dateset in self.make_datesets(start, end, size=size):
            if datesets:
                print dateset[-1]
                dateset_a, dateset_b = datesets[-1], dateset
                total_a = self.total_for_dateset(dateset_a)
                total_b = self.total_for_dateset(dateset_b)
                base_trend, base_error = self.calculate_trend(total_a, total_b)

                results = sorted(func(datesets[-1], dateset),
                                 lambda x, y: cmp(x[1] - base_trend, y[1] - base_trend),
                                 reverse=True)

                for obj, trend, error, total_b in results[:5]:
                    print obj, trend, error, total_b
                print

            datesets.append(dateset)


    def candidate_trend_for_datesets(self, dateset_a, dateset_b):
        candidates = (self.active_candidates(*dateset_a) | self.active_candidates(*dateset_b)).distinct()
        for candidate in candidates:
            total_a = self.obj_total_for_dateset(candidate, dateset_a)
            total_b = self.obj_total_for_dateset(candidate, dateset_b)
            trend, error = self.calculate_trend(total_a, total_b)
            yield (candidate, trend, error, total_b)


    def race_trend_for_datesets(self, dateset_a, dateset_b):
        fields = ['office', 'state', 'district', 'cycle', ]

        candidates = (self.active_candidates(*dateset_a) | self.active_candidates(*dateset_b)).distinct()
        races = set(candidates.values_list(*fields))

        for race in races:
            candidates = Candidate.objects.filter(**dict(zip(fields, race)))
            total_a, total_b = 0, 0
            for candidate in candidates:
                total_a += self.obj_total_for_dateset(candidate, dateset_a) or 0
                total_b += self.obj_total_for_dateset(candidate, dateset_b) or 0

            trend, error = self.calculate_trend(total_a, total_b)
            yield (race, trend, error, total_b)



    def make_datesets(self, start, end, size=1):
        curr = start
        while curr <= end:
            if curr + datetime.timedelta(size-1) > end:
                break
            yield self.dates_in_range(curr, curr + datetime.timedelta(size))
            curr += datetime.timedelta(1)

    def dates_in_range(self, start, end, step=1):
        """Generate a list of a dates within a range (inclusive).
        """
        curr = start
        dates = []
        while curr < end:
            dates.append(curr)
            curr += datetime.timedelta(days=step)
        return dates


    def total_for_dateset(self, dateset):
        return Expenditure.objects.filter(expenditure_date__in=dateset).aggregate(total=Sum('expenditure_amount'))['total']


    def committee_trend_for_datesets(self, dateset_a, dateset_b):
        """Calculate committee trends between two sets of dates.
        """
        committees = (self.active_committees(*dateset_a) | self.active_committees(*dateset_b)).distinct()
        for committee in committees:
            total_a = self.obj_total_for_dateset(committee, dateset_a)
            total_b = self.obj_total_for_dateset(committee, dateset_b)
            trend, error = self.calculate_trend(total_a, total_b)
            yield (committee, trend, error, total_b)


    def obj_total_for_dateset(self, obj, dateset):
        return obj.expenditure_set.filter(expenditure_date__in=dateset).aggregate(total=Sum('expenditure_amount'))['total']


    def active_committees(self, *dates):
        committee_ids = Expenditure.objects.filter(expenditure_date__in=dates).values_list('committee', flat=True)
        return Committee.objects.filter(id__in=committee_ids)


    def active_candidates(self, *dates):
        candidate_ids = Expenditure.objects.filter(expenditure_date__in=dates).values_list('candidate', flat=True)
        return Candidate.objects.filter(id__in=candidate_ids)


    def calculate_trend(self, a, b):
        a = a or 0
        b = b or 0
        total = a + b
        slope = b - a
        try:
            trend = slope * Decimal(str(math.log(1.0 + int(total))))
        except ValueError:
            return None, None
        try:
            error = 1.0/math.sqrt(total)
        except ZeroDivisionError:
            return None, None

        return trend, error
