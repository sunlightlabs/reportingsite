from recovery.millions.models import *
 
def filters(request):
    qs = Record.objects.filter(version_flag='F', recipient_role='P').exclude(status='x')
    recipient_state = qs.values_list('recipient_state', flat=True).distinct().order_by('recipient_state')
    awarding_agency_name = qs.values_list('awarding_agency_name', flat=True).distinct().order_by('awarding_agency_name')
    recipient_namee = qs.values_list('recipient_namee', flat=True).distinct().order_by('recipient_namee')
    pop_state_cd = qs.values_list('pop_state_cd', flat=True).distinct().order_by('pop_state_cd')
    pop_cong_dist = qs.values_list('pop_cong_dist', flat=True).distinct().order_by('pop_cong_dist')
    infrastructure_state_cd = qs.values_list('infrastructure_state_cd', flat=True).distinct().order_by('infrastructure_state_cd')

    filters = {'recipient_state': recipient_state, 'awarding_agency_name': awarding_agency_name, 'pop_state_cd': pop_state_cd, 'infrastructure_state_cd': infrastructure_state_cd, 'award_type': award_type, 'pop_cong_dist': pop_cong_dist }

    return { 'filters': filters }

