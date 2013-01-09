from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from outside_spending.models import Electioneering_93, Electioneering_94

def mark_as_superceded(filing_id):
    
    f93s = Electioneering_93.objects.filter(filing_number=filing_id)
    for f in f93s:
        f.superceded_by_amendment=True
        f.save()
    f94s = Electioneering_94.objects.filter(filing_number=filing_id)
    
    for f in f94s:
        f.superceded_by_amendment=True
        f.save()

class Command(BaseCommand):
    help = "Remove amended filings"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        # There's no programmatic way to remove amendments from this data. We're gonna have to ingest something else. 
        """
        mysql> select distinct filing_number, fec_id from outside_spending_electioneering_93 where amnd_ind != 'N';
        +---------------+-----------+
        | filing_number | fec_id    |
        +---------------+-----------+
        |        766315 | C30001952 |
        |        767351 | C30001655 |
        |        767476 | C30001655 |
        |        767479 | C30001655 |
    -    |        776628 | C30001945 |
    -    |        793291 | C30001952 |
    -    |        814346 | C30001028
        +---------------+-----------+
        4 rows in set (0.01 sec)
        """
        
        # order: amended filing : original filing
        amendment_table={
        # crossroads: 
        '767479':'764901',
        '767476':'764753',
        '767351':'764435',
        # american conservative union
        '766315':'764912',
        # PLANNED PARENTHOOD ACTION FUND INC. - C30001945
        '776628':'764197',
        '793291':'769723',
        '814346':'814213',
        }
        
        
        for a in amendment_table:
            print a, amendment_table[a]
            
        mark_as_superceded(amendment_table[a])    
            
        