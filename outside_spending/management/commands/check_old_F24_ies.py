# check for expenditures on F24's that are superceded but haven't been marked that way... 



from django.core.management.base import BaseCommand
from dateutil.parser import parse as dateparse

from outside_spending.models import Expenditure, F3X_Summary

class Command(BaseCommand):
    def handle(self, *args, **options):
        all_unsuperceded_f24s = Expenditure.objects.filter(filing_source='F24', superceded_by_f3x=False, superceded_by_amendment=False)
        for ie in all_unsuperceded_f24s:
            name = ie.committee.name if ie.committee else '-omitted-'
            if (ie.raw_committee_id == 'C00448696'):
                print "looking for date %s fec_name: %s filing_source %s" % (ie.expenditure_date, name, ie.filing_source)
            expenditure_date = ie.expenditure_date
            preexisting_f3xs=F3X_Summary.objects.filter(superceded_by_amendment=False, fec_id=ie.raw_committee_id, coverage_from_date__lte=expenditure_date, coverage_to_date__gte=expenditure_date)
            if len(preexisting_f3xs) > 0:
                # This transactions already been entered on an F3X. 
                print "%s Already covered in F3X: %s Details  %s %s %s $%s" % (ie.filing_number, preexisting_f3xs[0].filing_number, ie.committee_name, ie.raw_committee_id, ie.expenditure_date, ie.expenditure_amount )
                ie.superceded_by_amendment=True
                ie.superceded_by_f3x = True
                ie.superceding_f3x = preexisting_f3xs[0].filing_number
                ie.save()
            