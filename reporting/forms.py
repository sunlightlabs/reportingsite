from django import forms
from django.db.models import get_model
from tagging.forms import TagField
from reporting.widgets import CloudTagInput

class PostAdminModelForm(forms.ModelForm):
    tags = TagField(widget=CloudTagInput(), required=False)

    class Meta:
        model = get_model('reporting', 'post')


    class Media:
        css = {
            'all': ('jquery.autocomplete.css',)
        }
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js',
            'js/urlify.js',
            'rte/jquery.rte.js',
            'jquery.bgiframe.min.js'
        )
