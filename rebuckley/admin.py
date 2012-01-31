from models import *
from django.contrib import admin

class SuperPacAdmin(admin.ModelAdmin):
    
    fieldsets = (
        ("Reporting group data", {
            'fields': ('profile_url', 
                       'supporting', 
                       'display_name'),
                   
        }),
        ("FEC Data - Probably shouldn't change this", {
            'fields': ('fec_id', 
                       'fec_name'),
        }),

        
    )
    list_display = ('fec_name', 'total_indy_expenditures')
    
admin.site.register(IEOnlyCommittee, SuperPacAdmin)    
    