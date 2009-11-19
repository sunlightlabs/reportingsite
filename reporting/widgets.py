from django import forms
from django.db.models import get_model
from django.utils import simplejson
from django.utils.safestring import mark_safe
from tagging.models import Tag

from models import Post

#Post = get_model('reporting', 'post')

class CloudTagInput(forms.TextInput):
    class Media:
        css = {
            'all': ('jquery.autocomplete.css',)
        }
        js = (
            'js/jquery.js',
            'js/jquery.bgiframe.min.js',
            'js/jquery.ajaxQueue.js',
            'jquery.autocomplete.js'
        )

    def render(self, name, value, attrs=None):
        output = super(CloudTagInput, self).render(name, value, attrs)
        #page_tags = Tag.objects.usage_for_model(Post)
        return output + mark_safe(u'''<a onclick="tagswitch()" id="tagflip">Select tags</a><div id="tagcloud"></div>
                                    <script type="text/javascript">
                                    function tagswitch() {
                                        if( $('#tagcloud').html()=='') {
                                            $('#tagcloud').load('/tag/admin/');
                                        }    
                                        if( $('#tagflip').html()=='Select tags') {
                                            $('#tagflip').html('Hide tags');
                                            $('#tagcloud').toggle()
                                        }  else {
                                            $('#tagflip').html('Select tags');
                                            $('#tagcloud').toggle()
                                        }
                                    }
                                    function addtag(tagname) {
                                        $('#id_tags').val( tagname + ', ' + $('#id_tags').val() );
                                    }</script>''')

