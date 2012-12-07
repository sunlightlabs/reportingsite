from models import *
from django.contrib import admin
from django import forms

from tagging.fields import TagField
from forms import PostAdminModelForm
import settings


AUTHOR_GROUP = getattr(settings, 'BLOGDOR_AUTHOR_GROUP', None)

class CkeditorContentField(forms.Textarea):

    def render(self, name, value, attrs=None):
        if name == 'content':
            attrs.setdefault('class', 'ckeditor')
        return super(CkeditorContentField, self).render(name, value, attrs)


class PostAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('title', 
                       'slug', 
                       'author', ),
        }),
        (None, {
            'fields': ('content',
                       'excerpt',
                       'pullquote', ),
        }),
        (None, {
            'fields': ('whichsite', 
                       'date_published', 
                       'override_byline', 
                       'is_published', 
                       'is_favorite', 
                       'is_featured',
                       'show_on_index_pages',
                       'comments_enabled', 
                       'tags',
                       'fb_image_url' ),
        }),
    )

    list_display = ('title', 'author', 'is_favorite', 'is_published','date_published', 'whichsite', )
    list_filter = ('whichsite', 'is_published', 'author')
    list_display_links = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('author__username', 'author__first_name', 'title', 'content')
    actions = ('publish_posts', 'recall_posts', 'enable_comments', 'disable_comments')
    
    adminfiles_fields = ('content',)

    form = PostAdminModelForm

    formfield_overrides = {
            models.TextField: {'widget': CkeditorContentField, },
            models.CharField: {'widget': forms.TextInput(attrs={'size': '75'}) },
            }

    class Media:
        js = ('js/ckeditor/ckeditor.js', 
                )

    
    # return filtered author field

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        formfield = super(PostAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        formfield.choices = ((author.id, author.username) 
                                for author in User.objects.filter(is_active=True).order_by('username'))
        return formfield
    
    # post publishing actions
    
    def publish_posts(self, request, queryset):
        """
        Mark select posts as published and set date_published if it does not exist.
        """
        now = datetime.datetime.now()
        count = queryset.publish()
        self.message_user(request, "%i post(s) published" % count)
    publish_posts.short_description = "Publish posts"
    
    def recall_posts(self, request, queryset):
        """
        Recall published posts, but leave date_published as is.
        """
        count = queryset.recall()
        self.message_user(request, "%i post(s) recalled" % count)
    recall_posts.short_description = "Recall published posts"
    
    # enable or disable comment actions
    
    def enable_comments(self, request, queryset):
        count = queryset.update(comments_enabled=True)
        self.message_user(request, "Comments enabled on %i post(s)" % count)
    enable_comments.short_description = "Enable comments"

    def disable_comments(self, request, queryset):
        count = queryset.update(comments_enabled=False)
        self.message_user(request, "Comments disabled on %i post(s)" % count)
    disable_comments.short_description = "Disable comments"



admin.site.register(Post, PostAdmin)
admin.site.register(Upload)

class BackupAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'time' )
#admin.site.register(Backup, BackupAdmin)
