import csv
import sys
import MySQLdb

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.defaultfilters import slugify

from rebuckley.models import Committee

class Command(BaseCommand):
    args = '<cycle>'
    help = "Populate the committees table from the committee master file. Use a 2-digit cycle"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        cycle = args[0]
        cycle_year = 2000 + int(cycle)
        assert cycle, "You must enter a two-digit cycle"
        
        """      fields = [('committee_id', (1, 9)),
                 ('committee_name', (10, 99)),
                 ('designation', (231, 231)),
                 ('c_type', (232, 232)),
                 ('party', (233,235)),
                 ('filing_frequency', (236,236),
                 ('connected_org_name',(238,275),
                 ('candidate_id',(276,284)),
                 ('treasurer',(276,284)),
                 ('street_1',(276,284)),
                 ('street_2',(276,284)),
                 ('city',(276,284)),
                 ('zip',(276,284)),
                 ]
        """            
        fields = [('committee_id', (1, 9)),
                    ('committee_name', (10, 99)),
                    ('designation', (231, 231)),
                    ('c_type', (232, 232)),
                    ('party', (233,235)), 
                    ('filing_frequency', (236,236)),
                    ('connected_org_name',(238,275)),
                    ('candidate_id',(276,284))]
        
        data_filename = "rebuckley/data/%s/foiacm.dta" % (cycle)
        data_file = open(data_filename, "r")
        processed =0
        for line in data_file:
            print line 
            processed +=1
            data_dict = {}
            for fieldname, (start, end) in fields:
                data_dict[fieldname] = line[start-1:end].strip()
                print ("%s : '%s'" % (fieldname, data_dict[fieldname]))  
                
                
            try:
                #print data_dict['committee_id']
                existing_committee = Committee.objects.get(fec_id=data_dict['committee_id'])
                #print "Found committee: %s" % (data_dict['committee_id']) 
                pass
            except Committee.DoesNotExist:
                print "Creating %s" % (data_dict['committee_id'])
                
                """Not sure why but these models only accept blanks, not nulls."""
                
                try:
                    committee_slug = slugify(data_dict['committee_name'])
                except KeyError:
                    committee_slug = ''
                    
                try: 
                    name=data_dict['committee_name'] 
                except KeyError:
                    name=""
                    
                try:
                    party=data_dict['party']
                    #party = party.replace("(","")
                except KeyError:
                    party=""
                
                try:
                    designation=data_dict['designation']
                except KeyError:
                    designation=""

                try:
                    the_ctype=data_dict['c_type']
                except KeyError:
                    the_ctype=""

                try:
                    the_filing_frequency=data_dict['filing_frequency']
                except KeyError:
                    the_filing_frequency="" 
                    
                    
                try:
                    interest_group_cat=data_dict['interest_group_cat']
                except KeyError:
                    interest_group_cat=""                                               
        
                try:
                    connected_org_name=data_dict['connected_org_name']
                except KeyError:
                    connected_org_name=""
                    
                    
                try:
                    candidate_id=data_dict['candidate_id']
                    if candidate_id:
                        candidate_office=candidate_id[0]
                    else:
                        candidate_office=""
                except KeyError:
                    candidate_id=""    
                    candidate_office=""
                    
                print "Creating slug: %s with ctype:%s filing_frequency: ***%s***" % (committee_slug, the_ctype, the_filing_frequency)
                Committee.objects.create(
                            name=name,
                            fec_id=data_dict['committee_id'],
                            slug=committee_slug,
                            party=party,
                            designation=designation,
                            ctype=the_ctype,
                            filing_frequency=the_filing_frequency,                   
                            candidate_office=candidate_office,
                            interest_group_cat=interest_group_cat,
                            connected_org_name=connected_org_name,
                            candidate_id=candidate_id,
                            treasurer=line[100-1:137].strip(),
                            street_1=line[138-1:171].strip(),    
                            street_2=line[172-1:205].strip(), 
                            city=line[206-1:223].strip(), 
                            zip_code=line[226-1:230].strip())

                    