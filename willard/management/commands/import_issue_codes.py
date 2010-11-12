import csv
import sys

from django.core.management.base import BaseCommand

from willard.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        for row in csv.reader(sys.stdin, delimiter='|'):
            IssueCode.objects.create(code=row[0], issue=row[1].title())

