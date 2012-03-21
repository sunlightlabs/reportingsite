"""Flag the filing_headers and filing_rows that are amended. """


from django.core.management.base import BaseCommand

from outside_spending.models import Filing_Header, Filing_Rows

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        
        # get all the amended filings, ordered by filing number
        amended_filings = Filing_Header.objects.filter(is_amendment=True).order_by('filing_number')
        
        for af in amended_filings:
            print "Handling amended filing header: %s which amends %s" % (af.filing_number, af.amends_filing)
            
            
            
            original_filing=None
            try:
                original_filing = Filing_Header.objects.get(filing_number=af.amends_filing, is_amended=False)
                original_filing.is_amended=True
                original_filing.amended_by=af.filing_number
                original_filing.save()
            except Filing_Header.DoesNotExist:
                # we've already updated it, or the original predates our corpus
                print "Missing original filing: %s" % (af.amends_filing)
                
                
                
                
                
                
            # Are there are prior amendments (i.e. filings with a lower filing number)? If so, we need to make sure that they're marked as being amended too. 
            prior_amendments = Filing_Header.objects.filter(amends_filing=af.amends_filing).filter(is_amended=False).filter(filing_number__lt=af.filing_number)
            for pa in prior_amendments:
                print "** handling prior amendment"
                pa.is_amended=True
                pa.amended_by=af.filing_number
                pa.save()
                
                
        ## Now make sure that any child rows are also marked as superceded by amendment.
        print "Now setting amendment flag on child filing rows"    
        amended_rows = Filing_Rows.objects.filter(parent_filing__is_amended=True)
        for ar in amended_rows:
            ar.superceded_by_amendment=True
            ar.save()
            
            
    
