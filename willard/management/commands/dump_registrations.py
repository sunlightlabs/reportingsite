import csv
import sys

from django.core.management.base import BaseCommand

from willard.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        csv.writer(sys.stdout).writerow(['id',
                                         'registration_type',
                                         'registrant',
                                         'client',
                                         'received',
                                         'issues',
                                         'specific_issue', ])
        for registration in Registration.objects.all():
            csv.writer(sys.stdout).writerow(registration.as_csv())
