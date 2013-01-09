
from django.core.management.base import BaseCommand
from willard.management.commands import house_post_employment, senate_post_employment
from optparse import make_option
from datetime import datetime
from time import sleep

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
            make_option('-a', '--allyears',
                action='store_true',
                dest='allyears',
                default=False,
                help='Retrieve all records, not just the current year',
            ),
            make_option('-s', '--senate-only',
                action='store_true',
                dest='senate',
                default=False,
                help='Only grab senate records',
            ),
    )
    
    def handle(self, *args, **options):
        
        runallyears = options.get('allyears')
        senate = options.get('senate')
        if (senate):
            print "Only running senate"
        body = options.get('body')
        year = 2013
        has_year = False
        if args:
            year = int(args[0])
            if (year > 2006 and year < 2016 ):
                has_year = True
                print "Running year: %s" % (year)
        
        
        today = datetime.now()
        thisyear = today.year
        thisyearstring = str(thisyear)
        thismonthstring = str(today.month).zfill(2)
        thisdaystring = str(today.day).zfill(2)
        
        start_year = thisyear
        end_date = "%s/%s/%s" % (thismonthstring, thisdaystring, thisyearstring)
        start_date = "01/01/%s" % (thisyearstring)
        
        if (runallyears):
            start_year = 2008
            # House started doing this in Nov. 07.
            start_date = '11/01/2007'
            
        elif has_year:
            start_year = year
            thisyear = year
            start_date = "01/01/%s" % year
            end_date = "12/31/%s" % year
            
        if (not senate):
            print "retrieving house records for range %s - %s" % (start_date, end_date)
            scraper = house_post_employment.postEmploymentScraper()
            #scraper.scrape(start_date, end_date)
        
        for year in range(start_year, thisyear+1):
            print "retrieving senate records for year: %s" % (year)
            #senate_post_employment.get_senate(year)
            sleep(2)
        

            
            
        

        
        
