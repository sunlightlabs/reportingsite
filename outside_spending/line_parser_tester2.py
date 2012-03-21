import re
import os

from form_parser import form_parser
from filing import filing

from outside_spending_settings import filecache_directory

# load up a form parser
fp = form_parser()


def process_file(filingnum):
    f1 = filing(filingnum)
    f1.download()
    form = f1.get_form_type()
    version = f1.get_version()

    # only parse forms that we're set up to read
    
    if not fp.is_allowed_form(form):
        print "Not a parseable form: %s - %s" % (form, filingnum)
        return

    if (form!='F5'):
        return
    #print "Found parseable form: %s - %s" % (form, filingnum)
    #rows =  f1.get_all_rows()
    rows = f1.get_first_row()
    #print "rows: %s" % rows
    for row in rows:
        # the last line is empty, so don't try to parse it
        if len(row)>1:
            #print "in filing: %s" % filingnum
            parsed_line = fp.parse_form_line(row, version)
            print parsed_line

def run_loop():
    filecount = 0
    for d, _, files in os.walk(filecache_directory):
        for a in files:

            filecount += 1
            #print filecount
            filingnum = a.replace(".fec", "")
            if (int(filingnum) < 756587):
                #print "skipping %s" % (filingnum)
                continue

            #if filecount>10000:
            #    break

        
            process_file(filingnum)
       
#process_file(769297)
run_loop()