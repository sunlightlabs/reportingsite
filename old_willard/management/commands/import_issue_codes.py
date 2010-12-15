import csv
import sys

from django.core.management.base import BaseCommand

from willard.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        for row in csv.reader(sys.stdin, delimiter='|'):
            try:
                issue_code = IssueCode.objects.get(code=row[0])
            except IssueCode.DoesNotExist:
                IssueCode.objects.create(code=row[0], issue=row[1].title())
                continue
            issue_code.issue=row[1].title()
            issue_code.save()

