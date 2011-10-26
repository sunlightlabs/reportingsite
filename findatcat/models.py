from django.db import models
import tagging

class Link(object):
    title = models.CharField(max_length=128)
    url = models.URLField(verify_exists=False)
    description = models.TextField()
    
    class Meta:
        ordering = ('title',)
    
    def __unicode__(self):
        return self.title

tagging.register(Link)