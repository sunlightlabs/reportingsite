""" Scrape today's daily filings; or, with 'yesterday' as an arg, scrape yesterdays filings, or, with a datestring, scrape a previous day's filings... """

import urllib2
import re
import datetime


from urllib import urlencode
from optparse import make_option

from dateutil.parser import parse as dateparse

from django.core.management.base import BaseCommand, CommandError

from outside_spending.models import unprocessed_filing, processing_memo, Committee_Overlay, Filing_Scrape_Time

from outside_spending.read_FEC_settings import FILECACHE_DIRECTORY, USER_AGENT, FEC_DOWNLOAD, DELAY_TIME, MAX_FILING_KEY
from outside_spending.utils.fec_logging import fec_logger


# parser regexes -- it's cleaner to use regexes than html parsing
download_area_re = re.compile("<DL>(.+)<BR><P ALIGN=CENTER>",re.S)
committee_name_re = "<H4><A HREF='\/cgi-bin\/dcdev\/forms/(C\d+)\/'>(.*?)\s+-\s+C\d+\s*<\/A><\/H4>"
line_re = "&nbsp;&nbsp;(.+?)\n"
form_re = "<A HREF='\/cgi-bin\/dcdev\/forms\/(C\d+)\/(\d+)\/'>View<\/A>&nbsp;&nbsp;&nbsp;&nbsp;<A HREF='\/cgi-bin\/dcdev\/forms/DL\/\d+\/'>Download</A>&nbsp;&nbsp;\s+FEC-\d+\s+Form\s+(F.*?)\s+"
period_re = "-\s*period (\d\d\/\d\d\/\d\d\d\d)-(\d\d\/\d\d\/\d\d\d\d),"
filed_re = "filed\s+(\d\d\/\d\d\/\d\d\d\d)\s+"

my_logger=fec_logger()

def enter_filing(data_hash):
    print "\tentering %s" % (data_hash['filing_number'])
    is_superpac=False
    filing_created=False
    try:
        Committee_Overlay.objects.get(fec_id=data_hash['committee_id'], is_superpac=True)
        is_superpac=True
    except Committee_Overlay.DoesNotExist:
        pass
    
    try:
        unprocessed_filing.objects.get(filing_number=data_hash['filing_number'])
    except unprocessed_filing.DoesNotExist:
        thisobj = unprocessed_filing.objects.create(
            fec_id = data_hash['committee_id'],
            committee_name = data_hash['committee_name'],
            filing_number = data_hash['filing_number'],
            form_type = data_hash['form_type'],
            filed_date = data_hash['date_filed'],
            process_time = data_hash['process_time'],
            is_superpac=is_superpac
        )
        filing_created=True
        needs_saving=False
        try:
            thisobj.coverage_from_date = data_hash['date_from']
            needs_saving=True
        except KeyError:
            pass
        try:
            thisobj.coverage_to_date = data_hash['date_to']
            needs_saving=True
        except KeyError:
            pass
        if needs_saving:
            thisobj.save()
    
    # return true if a new filing was created
    return filing_created

def parse_response(response_html):
    
    current_pac_name = ''
    current_pac_id = ''
    
    results = []
    
    text_block = re.search(download_area_re, response_html)
    filer_chunks = text_block.group(1).split("<DT>")
    for chunk in filer_chunks:
        # we match an empty line or two 
        if len(chunk) < 3:
            continue
        #print "'%s'" % (chunk)
        committee_found = re.search(committee_name_re, chunk)
        current_pac_name = committee_found.group(2)
        current_pac_id = committee_found.group(1)
        #print "Found committee '%s' id: '%s'" % (current_pac_name, current_pac_id)
        
        forms = re.findall(line_re, chunk)
        for line in forms:
            #print "*** got line: %s " % (line)
            
            # remove the red color that's used to highlight amended forms:
            
            line = line.replace('<FONT COLOR ="#990000">', '')
            line = line.replace('</FONT>', '')
            formdetails = re.search(form_re, line)
            filing_number = formdetails.group(2)
            form_type = formdetails.group(3)
            this_id = formdetails.group(1)
            if (this_id != current_pac_id):
                my_logger.error('SCRAPE DAILY FILINGS: FORM MISMATCH ERROR!!')
                raise ("Form mismatch!!!")
                
            #print "Found details %s %s %s" % (formdetails.group(1), formdetails.group(2), formdetails.group(3) )
            
            period = re.search(period_re, line)
            date_from = None
            date_to = None
            if period:
                date_from = dateparse(period.group(1))
                date_to = dateparse(period.group(2))
                #print "Found period %s - %s " % (date_from, date_to)
            #else:
            #    print "** Couldn't find period in line %s" % line
                
            filing_info = re.search(filed_re, line)
            date_filed = dateparse(filing_info.group(1))
            #print "Date filed '%s'" % (date_filed)
            
            this_result={
                'committee_name': current_pac_name,
                'committee_id': current_pac_id,
                'filing_number': filing_number,
                'form_type': form_type,
                'date_filed': date_filed            
            }
            if (date_from):
                this_result['date_from']=date_from
                this_result['date_to']=date_to
            results.append(this_result)    
        
    return results

class Command(BaseCommand):
    
    
    requires_model_validation = False
    max_value = None
    
    def __init__(self):
        self.max_value = processing_memo.objects.get(message=MAX_FILING_KEY)


    def handle(self, *args, **options):
        
        date_to_run = None
        
        
        try:
            arg0 = args[0]
            
            if arg0.upper()=='YESTERDAY':
                date_to_run = datetime.date.today() - datetime.timedelta(days=1)
            else:
                date_to_run=dateparse(args[0])
        except IndexError:
            pass
                
        print "date to run is: %s" % date_to_run
        
        new_filings = 0
        temp_max = self.max_value.value
        
        
        my_logger.info('SCRAPE_DAILY_FILINGS - starting regular run')
        todays_date = date_to_run
        if not todays_date:
            today = datetime.date.today()
            todays_date = today.strftime("%m/%d/%Y")
            process_time = datetime.datetime.now()
        else:
            # assumes we're running it on an older date... 
            process_time = datetime.datetime(date_to_run.year, date_to_run.month, date_to_run.day, 23, 59)
            todays_date = date_to_run.strftime("%m/%d/%Y")
        
        my_logger.info("SCRAPE DAILY FILINGS: looking for filings from %s with process time of %s" % (todays_date, process_time))
        url = 'http://query.nictusa.com/cgi-bin/dcdev/forms/'
        values = {'comid' : 'C',
                  'name' : '',
                  'state' : '',
                  'rpttype' : '',
                  'date':todays_date,
                  'frmtype': '',
                  'submit': 'Send Query'}

        headers = {'User-Agent': USER_AGENT}   
        data = urlencode(values)       
        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req)
        filetoread = response.read()
        
        #filetoread = open("/Users/jfenton/reporting/reportingsitenew/reportingsite/outside_spending/scripts/sample2.html", 'r').read()
        results = parse_response(filetoread)

        for result in results:
            #print "Processing filing number: %s" % (int(result['filing_number']))
            
            # Test all entries.  
            result['process_time']=process_time             
            filing_entered = enter_filing(result)
            if filing_entered:
                new_filings += 1
            this_filing = int(result['filing_number'])
            if this_filing > temp_max:
                temp_max = this_filing

        # We're done processing, so set the max value
        
        self.max_value.value=temp_max
        self.max_value.save()
        now = Filing_Scrape_Time.objects.create()
        my_logger.info("SCRAPE_DAILY_FILINGS - completing regular run--created %s new filings" % new_filings)
                