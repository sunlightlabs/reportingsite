from django.template import Library
from outside_spending.models import Scrape_Time

register = Library()


@register.inclusion_tag('outside_spending/update_time.html')  
def updatetime():
    most_recent_scrape=Scrape_Time.objects.all().order_by('-run_time')[0]
    return {
    'most_recent_scrape':most_recent_scrape,
    }
    