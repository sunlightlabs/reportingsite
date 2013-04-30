import os
from dateutil.parser import parse as dateparse
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from willard.models import PostEmploymentNotice

dir_base = "/projects/reporting/src/"
temp_dir = dir_base + "reportingsite/willard/data"
zip_file_location = "http://clerk.house.gov/public_disc/post-employment/PostEmployment.zip"
temp_zip_location = temp_dir +  "/PostEmployment.zip"


def clean_entry(cellbit):
    cellbit = cellbit.replace("\r", "")
    cellbit = cellbit.replace("\n", "")    
    cellbit = cellbit.strip()
    cellbit = cellbit.upper()
    return cellbit

def download_and_unzip(process_files=False):
    
    curl_cmd = "curl -o \"%s\" \"%s\"" % (temp_zip_location, zip_file_location)
    print "curl cmd is: %s" % (curl_cmd)
    if process_files:
        os.system(curl_cmd)

    unzip_cmd = "unzip -o %s -d %s" % (temp_zip_location, temp_dir)
    print "unzip cmd is: %s" % (unzip_cmd)
    if process_files:
        os.system(unzip_cmd)
        

def process_file():
    # should create a text file
    unzipped_text_file = temp_dir + "/PostEmployment.txt"
    employment_file = open(unzipped_text_file, "r")
    is_first_line = True
    for line in employment_file:
        if not is_first_line:
            values = line.split("\t")
            #print len(values)
            name, office_name, begin_date, end_date = [clean_entry(x) for x in values]
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
            
            try:
                employee = PostEmploymentNotice.objects.create(**this_employee)
                print "Added employee: %s" % (employee)

            except IntegrityError:
                pass
            
        else:
            is_first_line = False

def run_house_scrape():
    download_and_unzip(process_files=True)
    process_file()
    
class Command(BaseCommand):
    body = "House"
    def handle(self, *args, **options):        
        download_and_unzip()
        process_file()
        
