from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.shortcuts import get_object_or_404

from outside_spending.models import Committee, unprocessed_filing, Filing_Scrape_Time


class FilingFeedBase(Feed):
    description_template = 'feeds/fec_filing_description.html'

    # What is this used for?
    def link(self, obj):
        return 'link'

    def description(self):
        return "Recent electronic campaign finance filings."
    
    def item_title(self, item):
        return  "FILING %s - %s" % (item.filing_number, item.get_form_name().upper() )
        
    def item_pubdate(self, item):
        return item.process_time

    def title(self):
        return "RECENT FILINGS FROM VARIOUS COMMITTEES"

class FilingFeed(FilingFeedBase): 
       
    def title(self, obj):
        return "RECENT FILINGS FROM: %s" % obj.name
        
    def get_object(self, request, committee_id):
        return get_object_or_404(Committee, fec_id=committee_id) 

    def items(self, obj):
        return unprocessed_filing.objects.filter(fec_id=obj.fec_id).order_by('-process_time')[:30]  

    
class FilingsFeed(FilingFeedBase):
    committee_list=[]
    
    def get_object(self, request, committee_ids):
        self.committee_list = committee_ids.split("-")
        return Filing_Scrape_Time.objects.all().order_by('-run_time')[0]

    def items(self, obj):
        return unprocessed_filing.objects.filter(fec_id__in=self.committee_list).order_by('-process_time')[:30]

class FilingsFormFeed(FilingFeedBase):
    committee_list=[]
    form_list=[]

    def get_object(self, request, committee_ids, form_types):
        self.committee_list = committee_ids.split("-")
        self.form_list=form_types.split("-")
        return Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    
    def description(self):
        return "Recent electronic finance filings of forms: " + " ".join(self.form_list)

    def items(self, obj):
        return unprocessed_filing.objects.filter(fec_id__in=self.committee_list, form_type__in=self.form_list).order_by('-process_time')[:30]
