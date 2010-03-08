from reporting.models import Post
from feedinator import Feed, FeedEntry
 
def latest_by_site(request):
    FLIT = Post.objects.filter(is_published=True, whichsite='FLIT')[:5] 
    PT = FeedEntry.objects.filter(feed__codename='partytime')[:5]
    SS = Post.objects.filter(is_published=True, whichsite='SS')[:5] 
    SLRG = Post.objects.filter(is_favorite=True, is_published=True, whichsite='SLRG')[:5] 

    return {'FLIT': FLIT, 'SS': SS, 'PT': PT, 'SLRG': SLRG }



from millions.models import *
 
def filters(request):
    baseq = Record.objects.filter(version_flag='F', recipient_role='P').exclude(status='x')
    recipient_state = baseq.values_list('recipient_state', flat=True).distinct().order_by('recipient_state')
    awarding_agency_name = baseq.values_list('awarding_agency_name', flat=True).distinct().order_by('awarding_agency_name')
    pop_state_cd = baseq.values_list('pop_state_cd', flat=True).distinct().order_by('pop_state_cd')
    infrastructure_state_cd = baseq.values_list('infrastructure_state_cd', flat=True).distinct().order_by('infrastructure_state_cd')
    project_activity_desc = baseq.values_list('project_activity_desc', flat=True).distinct().order_by('project_activity_desc')
    award_type = ['', 'Contract', 'Grant', 'Loan']
    pop_cong_dist = baseq.values_list('pop_cong_dist', flat=True).distinct().order_by('pop_cong_dist')

    filters = {'recipient_state': recipient_state, 'awarding_agency_name': awarding_agency_name, 'pop_state_cd': pop_state_cd, 'infrastructure_state_cd': infrastructure_state_cd, 'award_type': award_type, 'project_activity_desc': project_activity_desc,  'pop_cong_dist': pop_cong_dist }

    return { 'filters': filters }



