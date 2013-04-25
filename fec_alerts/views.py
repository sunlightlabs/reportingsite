# Create your views here.
import datetime

from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404, render_to_response
# in 1.3 there's django.shortcuts.render . D'oh!
from django.http import HttpResponse, Http404
from django.db.models import Sum, Min
from django.db.models import Q
from django.contrib.localflavor.us.us_states import STATE_CHOICES

from fec_alerts.models import Filing_Scrape_Time, new_filing, newCommittee
CYCLE='2014'

from outside_spending_2014.models import Committee

# should be fixed! 
significant_committees_list = ['C00431171', 'C00496497', 'C00496034', 'C00495820', 'C00010603', 'C00042366', 'C00000935', 'C00003418', 'C00027466', 'C00075820', 'C00431445']

def recent_fec_filings(request):
    
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    filings = new_filing.objects.all().order_by('-filing_number')[:50]
    title="Recent FEC Filings"
    explanatory_text="All recent electronic FEC filings. Filings made on paper are not included."
    
    return render_to_response('fec_alerts/recent_fec_filings.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )
    
def recent_ie_filings(request):

    filings = new_filing.objects.filter(form_type__in=['F5A', 'F5N', 'F24A', 'F24N']).order_by('-filing_number')[:50]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title="Recent Independent Expenditure Filings"
    explanatory_text="These are recent electronic FEC filings that show independent expenditures--specifically, forms F24 and F5."

    return render_to_response('fec_alerts/recent_fec_filings.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )
    

def significant_committees(request):

    filings = new_filing.objects.filter(fec_id__in=significant_committees_list).order_by('-filing_number')[:50]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title="Notable PAC Filings"
    explanatory_text="These are recent electronic FEC filings from major presidential candidates and party committees."

    return render_to_response('fec_alerts/recent_fec_filings.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )

def significant_committees_new(request):

    filings = new_filing.objects.filter(fec_id__in=significant_committees_list, form_type__in=['F3XN', 'F3N', 'F3PN']).order_by('-filing_number')[:50]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title="Monthly / Quarterly Filings From Major PACs"
    explanatory_text="These are recent monthly / quarterly electronic FEC filings from major presidential candidates and party committees. Amended filings are not included. "

    return render_to_response('fec_alerts/recent_fec_filings.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )    
def recent_superpac_filings(request): 

    filings = new_filing.objects.filter(is_superpac=True).order_by('-filing_number')[:50]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title='Super PAC Filings'
    explanatory_text="These are recent electronic FEC filings from super PACs."

    return render_to_response('fec_alerts/recent_fec_filings.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )   

def recent_superpac_filings_f3x(request): 

    filings = new_filing.objects.filter(is_superpac=True, form_type='F3XN').order_by('-filing_number')[:50]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title='Original Monthly / Quarterly Super PAC Filings'
    explanatory_text="These are new monthly / quarterly reports from super PACs (ie form F3XN). Amended filings are not included. "

    return render_to_response('fec_alerts/recent_fec_filings.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )
    
def recent_fec_filings_48hr_contrib(request):
    filings = new_filing.objects.filter(form_type__in=['F6N', 'F6A']).order_by('-filing_number')[:25]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title='48-hr Contribution Reports - FEC filings - Sunlight Foundation'
    explanatory_text="These 48 hour reports are used to disclose the receipt of last-minute contributions of $1,000 or more. Principal campaign committees must file these notices for contributions received after the 20th day, but more than 48 hours, before the day the candidate's election."

    return render_to_response('fec_alerts/recent_fec_filings.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )  

def recent_fec_filings_mobile(request):

    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    filings = new_filing.objects.all().order_by('-filing_number')[:25]
    title="Recent FEC Filings  - FEC filings - Sunlight Foundation"
    explanatory_text="All recent electronic FEC filings. Filings made on paper are not included."

    return render_to_response('mobile_test/fec_alerts_index.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )

def recent_fec_filings_ies(request):

    filings = new_filing.objects.filter(form_type__in=['F5A', 'F5N', 'F24A', 'F24N']).order_by('-filing_number')[:25]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title="Recent Independent Expenditures - FEC filings - Sunlight Foundation"
    explanatory_text="These are recent electronic FEC filings that show independent expenditures--specifically, forms F24 and F5."

    return render_to_response('mobile_test/fec_alerts_more.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )    

def recent_fec_filings_significant(request):

    filings = new_filing.objects.filter(fec_id__in=significant_committees_list).order_by('-filing_number')[:25]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title="Notable PACs  - FEC filings - Sunlight Foundation"
    explanatory_text="These are recent electronic FEC filings from major presidential candidates and party committees."

    return render_to_response('mobile_test/fec_alerts_more.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )

def recent_fec_filings_significant_new(request):

    filings = new_filing.objects.filter(fec_id__in=significant_committees_list, form_type__in=['F3XN', 'F3N', 'F3PN']).order_by('-filing_number')[:25]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title="Notable PACs  - FEC filings - Sunlight Foundation"
    explanatory_text="These are recent electronic monthly / quarterly filings from major presidential candidates and party committees."

    return render_to_response('mobile_test/fec_alerts_more.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )

def recent_fec_filings_superpacs(request): 

    filings = new_filing.objects.filter(is_superpac=True).order_by('-filing_number')[:25]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title='Super PAC Filings - FEC filings - Sunlight Foundation'
    explanatory_text="These are recent electronic FEC filings from super PACs."

    return render_to_response('mobile_test/fec_alerts_more.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )

def recent_fec_filings_superpacs_f3x(request): 

    filings = new_filing.objects.filter(is_superpac=True, form_type="F3XN").order_by('-filing_number')[:25]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title='Super PAC Filings - FEC filings - Sunlight Foundation'
    explanatory_text="These are recent electronic monthly / quarterly reports from super PACs."

    return render_to_response('mobile_test/fec_alerts_more.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )

def recent_fec_filings_48hr_contrib_mobile(request):
    filings = new_filing.objects.filter(form_type__in=['F6N', 'F6A']).order_by('-filing_number')[:25]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title='48-hr Contribution Reports - FEC filings - Sunlight Foundation'
    explanatory_text="These 48 hour reports are used to disclose the receipt of last-minute contributions of $1,000 or more. Principal campaign committees must file these notices for contributions received after the 20th day, but more than 48 hours, before the day the candidate's election."

    return render_to_response('mobile_test/fec_alerts_more.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )

def new_committees(request):
    today = datetime.datetime.today()
    month_ago = today - datetime.timedelta(days=30)
    committees=newCommittee.objects.filter(date_filed__gte=month_ago).order_by('-date_filed')
    return render_to_response('fec_alerts/new_committees.html', {
                'committees':committees,
                'explanatory_text':'These are committees formed within the last 30 days. It may take several days after a PAC is formed for details to be posted. Also see <a href="/fec-alerts/new-superpacs/">new super PACs</a>.',
                'title':'New Committees'
                })

def new_superpacs(request):
    today = datetime.datetime.today()
    month_ago = today - datetime.timedelta(days=30)
    committees=newCommittee.objects.filter(date_filed__gte=month_ago).filter(ctype='INDEPENDENT EXPENDITURE-ONLY').order_by('-date_filed')
    return render_to_response('fec_alerts/new_committees.html', {
                'committees':committees,
                'explanatory_text':'These are super PACs formed within the last 30 days. It may take several days after a PAC is formed for details to be posted. Also see <a href="/fec-alerts/new-committees/">all new committees</a>.',
                'title':'New Super PACs',
                })

def subscribe_to_alerts(request):

    return render_to_response('fec_alerts/subscribe.html',
        {'cycle':CYCLE,}
    )

def committee_search_html(request, cycle): 
    params = request.GET
    committees = None

    try:
        committee_name_fragment =  params['name']
        if len(committee_name_fragment) > 3:
            print committee_name_fragment


            committees = Committee.objects.filter(cycle=cycle).filter(Q(name__icontains=committee_name_fragment) | Q(related_candidate__fec_name__icontains=committee_name_fragment)).select_related()
        else:
            committees = None
    except KeyError:
        committees = None

    return render_to_response('fec_alerts/committee_search.html',
        {
        'committees':committees,
        }
    )

    


    