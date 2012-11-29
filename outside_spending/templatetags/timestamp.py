from django.template import Library
from outside_spending.models import Scrape_Time

register = Library()


@register.inclusion_tag('outside_spending/update_time.html')  
def updatetime():
    scrapes = Scrape_Time.objects.all().order_by('-run_time')
    if scrapes.count() == 0:
        return { 'most_recent_scrape': None }
    else:
        return { 'most_recent_scrape': scrapes[0] }
    
