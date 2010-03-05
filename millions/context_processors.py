from recovery.millions.models import *
 
def filters(request):
    recipient_state = Record.objects.values_list('recipient_state', flat=True).distinct().order_by('recipient_state')
    awarding_agency_name = Record.objects.values_list('awarding_agency_name', flat=True).distinct().order_by('awarding_agency_name')
    recipient_namee = Record.objects.values_list('recipient_namee', flat=True).distinct().order_by('recipient_namee')
    pop_state_cd = Record.objects.values_list('pop_state_cd', flat=True).distinct().order_by('pop_state_cd')
    infrastructure_state_cd = Record.objects.values_list('infrastructure_state_cd', flat=True).distinct().order_by('infrastructure_state_cd')
    award_type = ['', 'C', 'G', 'L']

    filters = {'recipient_state': recipient_state, 'awarding_agency_name': awarding_agency_name, 'pop_state_cd': pop_state_cd, 'infrastructure_state_cd': infrastructure_state_cd, 'award_type': award_type }

    return { 'filters': filters }

