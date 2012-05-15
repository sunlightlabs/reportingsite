from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

from outside_spending.models import Committee


def parse_file(filename):
    fields = [('committee_id', (1,9)),
              ('committee_name', (10, 99)),
              ('treasurer', (100, 137)),
              ('street1', (138, 171)),
              ('street2', (172, 205)),
              ('city', (206, 223)),
              ('state', (224, 225)),
              ('zipcode', (226, 230)),
              ('designation', (231, 231)),
              ('type', (232, 232)),
              ('party', (233, 235)),
              ('filing_frequency', (236, 236)),
              ('interest_group_category', (237, 237)),
              ('connected_org_name', (238, 275)),
              ('candidate_id', (276, 284))]
    records = []
    with file(filename, 'rU') as masterfile:
        for (line_num, line) in enumerate(masterfile, start=1):
            row = {}
            row['line_num'] = line_num
            for fieldname, (start, end) in fields:
                row[fieldname] = line[start-1:end].strip()
                
            row['slug'] = slugify(row['committee_name'][:50])
            records.append(row)

        print "%d records to process..." % len(records)

    return records
    
def get_or_create_committee(record):
    try:
        cmte = Committee.objects.get(fec_id=record['committee_id'])
        print ">>Found committee  %s %s" % (record['committee_id'], record['committee_name'])
        cmte.connected_org_name=record['connected_org_name']
        cmte.candidate_id=record['candidate_id']
        cmte.save()
    except Committee.DoesNotExist:
        print "Creating committee %s %s" % (record['committee_id'], record['committee_name'])
        cmte = Committee.objects.create(
            name=record['committee_name'],
            slug=record['slug'],
            fec_id=record['committee_id'],
            party=record['party'],
            treasurer=record['treasurer'],
            street_1=record['street1'],
            street_2=record['street2'],
            city=record['city'],
            zip_code=record['zipcode'],
            designation=record['designation'],
            ctype=record['type'],
            filing_frequency=record['filing_frequency'], 
            connected_org_name=record['connected_org_name'],
            candidate_id=record['candidate_id']
            )
            



class Command(BaseCommand):
    args = '<cycle>'
    help = "Populate the committees table from the committee master file. Use a 2-digit cycle"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        cycle = args[0]
        cycle_year = 2000 + int(cycle)
        assert cycle, "You must enter a two-digit cycle"
        data_filename = "outside_spending/data/%s/foiacm.dta" % (cycle)

        records = parse_file(data_filename)
        for record in records:
            get_or_create_committee(record)
            
      