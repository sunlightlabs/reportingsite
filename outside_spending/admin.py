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
            'fields': ('is_c4','political_orientation'),
            
        }),

        
    )
    
    list_display = (['name'])
    
admin.site.register(Committee_Overlay, CommitteeAdmin) 

