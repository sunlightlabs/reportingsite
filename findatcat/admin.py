from django.contrib import admin
from reportingsite.findatcat.models import Link, Category

admin.site.register(Link)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title','slug','description','tags')
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Category, CategoryAdmin)