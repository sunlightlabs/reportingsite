from millions.models import *
from django.contrib import admin


class RecordAdmin(admin.ModelAdmin):
    list_display = ('awarding_agency_name', 'project_name', 'award_amount', 'total_fed_arra_exp', 'pop_state_cd','number_of_jobs')
    list_filter = ('award_type', 'funding_agency_name')

admin.site.register(Record, RecordAdmin)
