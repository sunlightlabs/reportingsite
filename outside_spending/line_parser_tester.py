from line_parser import line_parser
from filing import filing

import re
import os

from outside_spending_settings import filecache_directory

# problem lines: 

# 'H4' - see 703845 - maybe it should be SH4 ? 
# 'H1' ; 'H3' 703886
# F3Z

# 703980

# what forms can we parse
allowed_forms = {
    'F3':1,
    'F3X':1,
    'F3P':1,
    'F9':1,
    'F5':1,
    'F24':1
}

# do the ones we care about work? 


f3p = line_parser('F3P')

# F3X -- how do we distinguish sc1 vs sc  1 ? 
f3x = line_parser('F3X')
sa = line_parser('SchA')
sb = line_parser('SchB')
sc1= line_parser('SchC1')
sc2= line_parser('SchC2')
sc= line_parser('SchC')
sd= line_parser('SchD')
se= line_parser('SchE')
sf=line_parser('SchF')

# F24 

f24 = line_parser('F24')

#F9

f9 = line_parser('F9')
f91= line_parser('F91')
f92= line_parser('F92')
f93= line_parser('F93')
f94= line_parser('F94')

f5= line_parser('F5')
f57= line_parser('F57')

f3 = line_parser('F3')
f3s = line_parser('F3S')
text = line_parser('TEXT')

# match form type to appropriate parsers; must be applied with re.I
# the leading ^ are redundant if we're using re.match
line_dict = {
    '^SA': sa,
    '^SB':sb,
    '^SC':sc,
    '^SC1':sc1,
    '^SC2':sc2,
    '^SD':sd,
    '^SE':se,
    '^SF':sf,
    '^F3X[A|N|T]':f3x,
    '^F3P[A|N|T]':f3p,
    '^F3S':f3s,
    '^F3[A|N|T]$':f3,
    '^F91':f91,
    '^F92':f92,
    '^F93':f93,
    '^F94':f94,
    '^F9':f9,
    '^F57':f57,
    '^F5':f5,
    '^TEXT':text,
    '^F24':f24
}

# we gotta test them in the correct order, and if it's a match pull the line parser from line_dict
# these must be an *EXACT MATCH* to the way they appear in the line_dict above.
regex_array = ['^SA', '^SB', '^SC', '^SC1', '^SC2', '^SD', '^SE', '^SF', '^F3X[A|N|T]', '^F3P[A|N|T]',  '^F3S', '^F3[A|N|T]$', '^F91', '^F92', '^F93', '^F94', '^F9', '^F57', '^F5', '^TEXT', '^F24']

           

def parse_form_line(line_array, version):
    #print "Trying to parse with v=%s line array=%s " % (version, line_array)
    form_type = line_array[0].replace('"','').upper()
    found_parser = False
    
    # Ignore problem lines
    if (form_type=='H4' or form_type=='H1' or form_type=='H2' or form_type =='H3' or form_type=='H5' or form_type=='H6' or form_type=='F3Z'  or form_type=='F3ZT'  or form_type=='F3ZA'  or form_type=='F3ZN' or form_type=='SL'):
        return None
    
    for regex in regex_array:
        if (re.match(regex,form_type, re.I)):
            #print "**Got match with regex: %s" % (regex)
            parser = line_dict[regex]
            #print "parser = %s" % parser
            parsed_line = parser.parse_line(line_array, version)
            #print "parsed line has len %s and is: %s" % (len(parsed_line), parsed_line)
            found_parser=True
    if not found_parser:
        raise Exception ("Couldn't find parser for form type %s, v=%s" % (form_type, version))
    
        

def process_file(filingnum):
    f1 = filing(filingnum)
    f1.download()
    form = f1.get_form_type()
    version = f1.get_version()

    try:
        allowed_forms[form]
    except KeyError:
        print "Not a parseable form: %s - %s" % (form, filingnum)
        return

    #print "Found parseable form: %s - %s" % (form, filingnum)
    rows =  f1.get_all_rows()
    #print "rows: %s" % rows
    for row in rows:
        # the last line is empty
        if len(row)>1:
            #print "in filing: %s" % filingnum
            parse_form_line(row, version)
    

def run_loop():
    filecount = 0
    for d, _, files in os.walk(filecache_directory):
        for a in files:

            filecount += 1
            print filecount
            filingnum = a.replace(".fec", "")
            if (int(filingnum) < 756587):
                print "skipping %s" % (filingnum)
                continue

            #if filecount>10000:
            #    break

        
            process_file(filingnum)
       
#process_file(769297)
run_loop()