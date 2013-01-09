""" Scrape house clerk pages. Annoying asp.net requires setting viewstate and eventvalidation, with a particular
    set of args each time. 
"""

import re
import requests
import urllib
from time import sleep
import lxml.html
from dateutil.parser import parse as dateparse

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from willard.models import PostEmploymentNotice

headers = {}
headers['User-Agent'] = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'

def slurp(url, params={}, method='GET'):
    response = requests.request(method, url, data=params, headers=headers, allow_redirects=True)
    assert response.status_code == 200, 'Unable to retrieve {0}, method {1}, status {2}'.format(url, method, response.status_code)
    print "headers received: %s" % response.headers
    print "headers sent: %s" % response.request.headers
    
    return response.content

def get_validation(rawhtml):
    validre = re.compile(r'id="__EVENTVALIDATION" value="(.*?)"')
    validation_result = re.search(validre, rawhtml)
    if validation_result:
#        print "validation is: %s" % validation_result.group(1)
        return validation_result.group(1)
    return None
    
def get_viewstate(rawhtml):
    viewstatere = re.compile(r'name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)"')
    viewstatere_result = re.search(viewstatere, rawhtml)
    if viewstatere_result:
#        print "view state found is: %s" % viewstatere_result.group(1)
        return viewstatere_result.group(1)
    return None
    
    
def count_result_pages(html):
    # results are paginated, w 20 results per page. 
    resultsre = re.compile(r'class\=\"searchRecords\">Records \d+ through \d+ of (\d+)<\/span>')
    found = re.search(resultsre, html)
    total_results = int(found.group(1))
    pages = total_results / 20
    if (total_results % 20 > 0):
        pages += 1
    print "Total result pages = %s" % (pages)
    return pages
    
def makeparams(date0, date1, validation, viewstate, event_target='', hasSearch=True):
    params = {

        'ctl00$cphMain$txbTermination_date0':date0,
        'ctl00$cphMain$txbTermination_date1':date1,
        '__VIEWSTATE':viewstate,
        '__EVENTVALIDATION':validation,
        '__VIEWSTATEENCRYPTED':'',
        '__EVENTTARGET':event_target,
        '__EVENTARGUMENT':'',
    }
    
    if hasSearch:
        params['ctl00$cphMain$btnSearch']='Search'
    return params

def clean_entry(htmlbit):
    htmlbit = htmlbit.replace("\r", "")
    htmlbit = htmlbit.replace("\n", "")    
    htmlbit = htmlbit.strip()
    htmlbit = htmlbit.upper()
    return htmlbit
    
class postEmploymentScraper():

    def __init__(self):
        
        self.save_files = False
        self.sleep_time = 2
        self.view_state = None
        self.eventvalidation = None
        self.href = 'http://clerk.house.gov/public_disc/employment.aspx'
        self.page_num = 0
        self.total_result_pages = 0
        # view states are associated with 5-page spans...
        self.total_page_groups = 0
        
        self.headers = headers
        # if saving files, they'll go here:
        self.file_dir = "pages_scraped/"
    
    def _set_states(self, rawhtml):
        self.view_state = get_viewstate(rawhtml)
        self.eventvalidation = get_validation(rawhtml)
        
    def _set_state_from_search(self):
        """ Set the view state etc by scraping the main search page. """
        
        this_html = slurp(self.href)
        self._set_states(this_html)

    def _write_file(self, raw_html, page_no, date_start, date_end):
        filenameraw = "pe_" + str(page_no) + "_" + date_start + "_" + date_end + ".html"
        filenameraw = filenameraw.replace("/", "-")
        filename = self.file_dir + filenameraw
        outf = open(filename, 'w')
        # todo: parsethefile
        outf.write(raw_html)
        outf.close()

        
    def _parse_page(self, rawhtml):
        doc = lxml.html.fromstring(rawhtml)
        table = doc.cssselect('#search_results')[0]
        for row in table.cssselect('tr')[1:]:
            try:
                name, office_name, begin_date, end_date = [clean_entry(x.text) for x in row.getchildren()]
                print "name %s office_name %s begin_date %s end_date %s" % (name, office_name, begin_date, end_date)
            except ValueError:
                continue    
                
            try:
                last, first = name.split(',')
            except ValueError:
                last = name
                first = ''
            this_employee = {'first': first.strip(),
                       'last': last.strip(),
                       'middle': '',
                       'office_name': office_name,
                       'begin_date': dateparse(begin_date),
                       'end_date': dateparse(end_date),
                       'body': 'House',
                        }
                        
            # Will throw an error if these fields are repeated: 'body', 'first', 'last', 'office_name',
            try:
                employee = PostEmploymentNotice.objects.create(**this_employee)
                print "Added employee: %s" % (employee)
                
            except IntegrityError:
                pass

            
        
    def _get_first_page(self, date_start, date_end):
        params = makeparams(date_start, date_end, self.eventvalidation, self.view_state)
        print "Scraping with params: \n%s" % (params)
        doc = slurp(self.href, params, method='POST')
        # set view state etc
        self._set_states(doc)
        self._parse_page(doc)
        # write file out
        if (self.save_files):
            write_file(doc, '0', date_start, date_end)
        self.page_num += 1
        
        # figure out how many pages there are of results
        self.total_result_pages = count_result_pages(doc)
        self.total_page_groups = self.total_result_pages / 5
        if ( self.total_result_pages % 5 > 0):
            self.total_page_groups += 1
        
    def _get_additional_page(self, date_start, date_end, page_no, actual_page):
        # Assumes page_no < 100
        event_target='ctl00$cphMain$DataPager1$ctl01$ctl%02d' % page_no 
        params = makeparams(date_start, date_end, self.eventvalidation, self.view_state, event_target=event_target, hasSearch=False)
        print "Scraping with params: \n%s" % (params)
        doc = slurp(self.href, params, method='POST')
        # set view state etc
        self._set_states(doc)
        self._parse_page(doc)
        if (self.save_files):
            write_file(doc, actual_page, date_start, date_end)
        
    def scrape(self, start_date, last_date, save_files=False):
        self.save_files = save_files
        # first set the view state etc from the search page:
        self._set_state_from_search()
        print "Sleeping %s sleep time" % (self.sleep_time)
        sleep(self.sleep_time)
        
        # Get the search page--this has search in the params. 
        self._get_first_page(start_date, last_date)
        
        
        for page_group in range(0,self.total_page_groups):
            print "Handling page group %s" % page_group
            for additional_page in (1,2,3,4,5):
                """ Clicking on page 5 gives you the first page of the next 'result set' """
                if self.page_num < self.total_result_pages:
                    print "Getting page %s actual page %s" % (additional_page, self.page_num)
                    self._get_additional_page(start_date, last_date, additional_page, self.page_num)
                    print "Sleeping %s sleep time" % (self.sleep_time)
                    sleep(self.sleep_time)
                    self.page_num += 1
        
        
if __name__ == "__main__":
    scraper = postEmploymentScraper()
    ## needs to be MM/DD/YYYY 
    start_date = '08/01/2012'
    last_date = '01/31/2013'
    scraper.scrape(start_date, last_date)
        
        
        
        