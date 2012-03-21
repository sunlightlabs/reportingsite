import MySQLdb

from django.core.management.base import BaseCommand, CommandError

from outside_spending.models import *
from django.db.models import *

dbcfg = settings.DATABASES['default']
assert 'mysql' in dbcfg['ENGINE'].lower(), "The import_crp_donors command requires a MySQL database."
cursor = MySQLdb.Connection(dbcfg['HOST'], dbcfg['USER'], dbcfg['PASSWORD'], dbcfg['NAME']).cursor()

def purge_contribs_by_filing_number(filing_num):
    old_contribs = Contribution.objects.filter(filing_number=filing_num)
    for oc in old_contribs:
        oc.delete()

class Command(BaseCommand):
    help = "Removes amended reports, and those that don't fit our time scale"
    requires_model_validation = False


    def handle(self, *args, **options):
        
        old_summaries = F3X_Summary.objects.filter(coverage_to_date__lte='2011-01-01')
        for os in old_summaries:
            print "Deleting F3X: %s %s-%s %s" % (os.committee_name, os.coverage_from_date, os.coverage_to_date, os.amended)
            purge_contribs_by_filing_number(os.filing_number)
        
            os.delete()
            
        old_contribs = Contribution.objects.filter(contrib_date__lte='2011-01-01')    
        for oc in old_contribs:
            oc.delete()    
            
        query = "select count(*), fec_id, coverage_to_date from rebuckley_f3x_summary group by fec_id, coverage_to_date"
        cursor.execute(query)
        rows = cursor.fetchall()
        for r in rows:
            if r[0] > 1:
                # We've got duplicates, probably because of amendments.
                fec_id = r[1]
                todate = r[2]
                
                summaries = F3X_Summary.objects.filter(coverage_to_date=todate, fec_id=fec_id).order_by('-filing_number')
                for (i, s) in enumerate(summaries):
                    if (i==0 and s.amended==0):
                        raise Exception("most recent filing isn't amended -- lookes like an error")
                    if (i>0):
                        print "Candidate for deletion: %s %s " % (s.fec_id, s.amended)
                        purge_contribs_by_filing_number(s.filing_number)
                        s.delete()
                        