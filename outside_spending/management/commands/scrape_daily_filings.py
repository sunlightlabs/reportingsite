import urllib2
import re
import datetime


from urllib import urlencode
from dateutil.parser import parse as dateparse

from django.core.management.base import BaseCommand, CommandError

from outside_spending.models import unprocessed_filing, processing_memo, Committee_Overlay

from outside_spending.read_FEC_settings import FILECACHE_DIRECTORY, USER_AGENT, FEC_DOWNLOAD, DELAY_TIME, MAX_FILING_KEY


# parser regexes -- it's cleaner to use regexes than html parsing
download_area_re = re.compile("<DL>(.+)<BR><P ALIGN=CENTER>",re.S)
committee_name_re = "<H4><A HREF='\/cgi-bin\/dcdev\/forms/(C\d+)\/'>(.*?)\s+-\s+C\d+\s*<\/A><\/H4>"
line_re = "&nbsp;&nbsp;(.+?)\n"
form_re = "<A HREF='\/cgi-bin\/dcdev\/forms\/(C\d+)\/(\d+)\/'>View<\/A>&nbsp;&nbsp;&nbsp;&nbsp;<A HREF='\/cgi-bin\/dcdev\/forms/DL\/\d+\/'>Download</A>&nbsp;&nbsp;\s+FEC-\d+\s+Form\s+(F.*?)\s+"
period_re = "-\s*period (\d\d\/\d\d\/\d\d\d\d)-(\d\d\/\d\d\/\d\d\d\d),"
filed_re = "filed\s+(\d\d\/\d\d\/\d\d\d\d)\s+"

def enter_filing(data_hash):
    print "\tentering %s" % (data_hash['filing_number'])
    is_superpac=False
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
    help = "Scrape daily filings; "
    requires_model_validation = False
    max_value = None
    
    def __init__(self):
        self.max_value = processing_memo.objects.get(message=MAX_FILING_KEY)


    def handle(self, *args, **options):
        
                
        temp_max = self.max_value.value
        process_time = datetime.datetime.now()
        
        print "Looking for filings higher than: %s" % (self.max_value.value)
        
        today = datetime.date.today()
        todays_date = today.strftime("%m/%d/%Y")
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
            print "Processing filing number: %s" % (int(result['filing_number']))
            
            # Test all entries.  
            result['process_time']=process_time             
            enter_filing(result)
            this_filing = int(result['filing_number'])
            if this_filing > temp_max:
                temp_max = this_filing

        # We're done processing, so set the max value
        
        self.max_value.value=temp_max
        self.max_value.save()
                