""" This overrides old data with new data -- it's parent is pop_committees_force_override """


from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

from outside_spending_2014.models import Committee
from outside_spending_2014.read_FEC_settings import DATA_DIR

def parse_file(filename):
    fields = ['committee_id','committee_name', 'treasurer', 'street1', 'street2','city','state', 'zipcode', 'designation', 'type', 'party', 'filing_frequency', 'interest_group_category', 'connected_org_name', 'candidate_id']
    

    records = []
    with file(filename, 'rU') as masterfile:
        for (line_num, line) in enumerate(masterfile, start=1):
            row = {}
            row['line_num'] = line_num
            line = line.rstrip("\n")
            data_fields = line.split("|")
            for cell, fieldname in enumerate(fields):
                row[fieldname] = data_fields[cell]
                
            row['slug'] = slugify(row['committee_name'][:50])
            records.append(row)
            
            row['is_superpac'] = False
            row['is_hybrid'] = False
            row['is_noncommittee'] = False
            
            #'pure' super pacs
            if row['type'] in ['O', 'U']: 
                row['is_superpac'] = True
            
            # hybrid pacs 
            elif row['type'] in ['V', 'W']:
                row['is_hybrid'] = True  
                          
            # independent spenders who aren't committees
            elif row['type'] == 'I':
                row['is_noncommittee'] = True
            
            

        print "%d records to process..." % len(records)
    return records
    
def get_or_create_committee(record,cycle):
    try:
        cmte = Committee.objects.get(fec_id=record['committee_id'], cycle=cycle)
        cmte.name=record['committee_name']
        cmte.slug=record['slug']
        cmte.party=record['party']
        cmte.treasurer=record['treasurer']
        cmte.street_1=record['street1']
        cmte.street_2=record['street2']
        cmte.city=record['city']
        cmte.state_race=record['state']
        cmte.zip_code=record['zipcode']
        cmte.designation=record['designation']
        cmte.ctype=record['type']
        cmte.filing_frequency=record['filing_frequency'] 
        cmte.connected_org_name=record['connected_org_name']
        cmte.candidate_id=record['candidate_id']
        cmte.interest_group_cat = record['interest_group_category']
        cmte.is_superpac = record['is_superpac']
        cmte.is_noncommittee = record['is_noncommittee']
        cmte.is_hybrid = record['is_hybrid']
        cmte.save()
    except Committee.DoesNotExist:
        print "Creating committee %s %s" % (record['committee_id'], record['committee_name'])
        cmte = Committee.objects.create(
            name=record['committee_name'],
            cycle=cycle,
            slug=record['slug'],
            fec_id=record['committee_id'],
            party=record['party'],
            treasurer=record['treasurer'],
            street_1=record['street1'],
            street_2=record['street2'],
            city=record['city'],
            state_race=record['state'],
            zip_code=record['zipcode'],
            designation=record['designation'],
            ctype=record['type'],
            filing_frequency=record['filing_frequency'], 
            connected_org_name=record['connected_org_name'],
            candidate_id=record['candidate_id'],
            interest_group_cat = record['interest_group_category'],
            is_superpac = record['is_superpac'],
            is_noncommittee = record['is_noncommittee'],
            is_hybrid = record['is_hybrid'],
            )
            



class Command(BaseCommand):
    args = '<cycle>'
    help = "Populate the committees table from the committee master file. Use a 2-digit cycle"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        cycle = args[0]
        cycle_year = 2000 + int(cycle)
        cycle_string = str(cycle_year)
        assert cycle, "You must enter a two-digit cycle"
        data_filename = "%s/%s/cm.txt" % (DATA_DIR, cycle)

        records = parse_file(data_filename)
        for record in records:
            get_or_create_committee(record, cycle_string)
            
      