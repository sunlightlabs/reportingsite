from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from scrapers import *


class Command(BaseCommand):

    args = '<agency agency ...>'
    help = """Scrape meeting logs from the specified agency

Valid agencies are:
    fdic 
    treasury 
    cftc 
    federal_reserve 
    sec
"""

    option_list = BaseCommand.option_list + (
            make_option('--special',
                action='store_true',
                dest='special',
                default=False,
                help='Use special parser',
            ),
        )

    def handle(self, *args, **options):
        if not args:
            raise CommandError('You must supply at least one agency name')

        scrapers = {'fdic': FDICScraper,
                    'cftc': CFTCScraper,
                    'sec': SECScraper,
                    'federal_reserve': FedreserveScraper,
                    'treasury': TreasuryScraper, 
                    }

        for agency in args:
            scraper = scrapers.get(agency)()
            scraper.scrape()
