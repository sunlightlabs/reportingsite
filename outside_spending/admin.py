from django.contrib import admin
from models import Committee_Overlay


#admin.site.disable_action('delete_selected')

class CommitteeAdmin(admin.ModelAdmin):
    # readonly_fields appears to be busted


    search_fields = ('name',)
    fieldsets = (
        ("From FEC", {
            'fields': ('name',),
                   
        }),
        ("Human-verified data", {
            'fields': ('org_status','political_orientation', 'political_orientation_verified'),
            
        }),

        
    )
    
    list_display = (['name', 'cash_on_hand', 'is_superpac', 'political_orientation', 'political_orientation_verified'])
    
admin.site.register(Committee_Overlay, CommitteeAdmin) 

