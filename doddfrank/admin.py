from django.contrib import admin
from doddfrank.models import Agency, Meeting, Attendee, Organization


admin.site.register(Agency)

class MeetingAdmin(admin.ModelAdmin):
    list_display = ['agency', 'date', 'topic', 'import_hash', 'attendee_hash']
    #fields = ('agency', 'date', 'topic', 'import_hash', 'attendee_hash', 'attendee_list')

admin.site.register(Meeting, MeetingAdmin)


class AttendeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'org']

admin.site.register(Attendee, AttendeeAdmin)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Organization, OrganizationAdmin)

