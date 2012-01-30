import csv
import sys
import MySQLdb

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.defaultfilters import slugify

from rebuckley.models import Candidate
#from name_cleaver import PoliticianNameCleaver

#dbcfg = settings.DATABASES['default']
#assert 'mysql' in dbcfg['ENGINE'].lower(), "Requires a MySQL database."
#cursor = MySQLdb.Connection(dbcfg['HOST'], dbcfg['USER'], dbcfg['PASSWORD'], dbcfg['NAME']).cursor()


class Command(BaseCommand):
    args = '<cycle>'
    help = "Populate the candidates table from the candidate master file. Use a 2-digit cycle"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        cycle = args[0]
        cycle_year = 2000 + int(cycle)
        assert cycle, "You must enter a two-digit cycle"
        
        fields = [('fec_id', (1, 9)),
                  ('fec_name', (10, 47)),
                  ('party', (48, 50)),
                  #('filler', (51, 53)),
                  #('party', (54, 56)),
                  ('seat_status', (57, 57)),
                  #('filler', (58, )),
                  ('candidate_status', (59, 59)),
                  ('state_address', (146, 147)),
                  ('zipcode', (148, 152)),
                  ('campaign_comm', (153, 161)),
                  ('election_year', (162, 163)),
                  ('current_district', (164, 165)), ]

        data_filename = "rebuckley/data/%s/foiacn.dta" % (cycle)
        data_file = open(data_filename, "r")
        for line in data_file:
            data_dict = {}
            for fieldname, (start, end) in fields:
                data_dict[fieldname] = line[start-1:end].strip()
                #print ("%s : %s" % (fieldname, data_dict[fieldname]))
                
            try:
                existing_candidate = Candidate.objects.get(fec_id=data_dict['fec_id'], cycle=cycle_year)
            except Candidate.DoesNotExist:
                
                #cleaved_name = str(PoliticianNameCleaver(data_dict['fec_name']).parse())
                candidate_slug = slugify(data_dict['fec_name'])
                
                # Name cleaver doesn't quite work with fec data:
                # TAUZIN, WILBERT J II --> Wilbert J Ii Tauzin
                ## Actually, Alison fixed the first one after
                # SCALISE, STEVE MR. --> Steve Mr. Scalise
                # RADOSTA, "JACK" --> Radosta
                # so I'm skipping it.
                
                # office is the first digit of the fec_id (?)
                office = data_dict['fec_id'][0]
                
                print "Adding candidate with name: %s id: %s" % (data_dict['fec_name'], data_dict['fec_id'])
                Candidate.objects.create(
                            cycle=cycle_year,
                            fec_id=data_dict['fec_id'],
                            fec_name=data_dict['fec_name'],
                            party=data_dict['party'],
                            office=office,
                            seat_status=data_dict['seat_status'],
                            candidate_status=data_dict['candidate_status'],
                            state_address=data_dict['state_address'],
                            district=data_dict['current_district'],
                            slug=candidate_slug,
                            campaign_com_fec_id=data_dict['campaign_comm']
                            
                                        )
                
                
        