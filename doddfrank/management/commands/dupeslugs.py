from collections import defaultdict

from doddfrank.views import _list_organizations

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify


class Command(BaseCommand):

    def handle(self, *args, **options):
        slugs = defaultdict(list)
        for organization in _list_organizations():
            slugs[slugify(organization)].append(organization)

        slugs = [x for x in slugs.items() if len(x[1]) > 1]
        for k, v in slugs:
            print k
            for i in v:
                print '\t', i
            print
