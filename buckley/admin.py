from buckley.models import *
from django.contrib import admin

class CommitteeAdmin(admin.ModelAdmin):
    pass

class PayeeAdmin(admin.ModelAdmin):
    pass

class CandidateAdmin(admin.ModelAdmin):
    pass

class ExpenditureAdmin(admin.ModelAdmin):
    pass

admin.site.register(Committee, CommitteeAdmin)
admin.site.register(Payee, PayeeAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Expenditure, ExpenditureAdmin)
