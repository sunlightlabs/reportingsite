from django import forms
from django.db.models import get_model
from tagging.forms import TagField
from reporting.widgets import CloudTagInput

from django.contrib.admin import widgets
from adminfiles.utils import render_uploads

from models import Post
#from tagging.forms import TagAdminForm
from django import forms

class PostAdminModelForm(forms.ModelForm):
    tags = TagField(widget=CloudTagInput(), required=False)

    date_published = forms.DateTimeField(widget=widgets.AdminSplitDateTime)

    def save(self, force_insert=False, force_update=False, commit=True):
        m = super(PostAdminModelForm, self).save(commit=False)
        # do custom stuff
        #if commit:
        m.content = render_uploads(m.content)
        print render_uploads(m.content)
        m.save()
        return m

    class Meta:
        model = Post


    class Media:
        css = {
            'all': ('jquery.autocomplete.css',)
        }
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js',
            'js/urlify.js',
            'rte/jquery.rte.js',
            'jquery.bgiframe.min.js',

            '/js/RelatedObjectLookups.js', '/js/calendar.js', '/js/DateTimeShortcuts.js'
        )



