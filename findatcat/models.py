from django.db import models
from django.template.defaultfilters import slugify

class Category(models.Model):
    title = models.CharField(max_length=64)
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)
    tags = models.TextField(blank=True)

    class Meta:
        ordering = ('title',)

    def __unicode__(self):
        return self.title
    
    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Category, self).save(**kwargs)
    
    def tag_list(self):
        return [t.strip() for t in self.tags.split(',')]

class Link(models.Model):
    title = models.CharField(max_length=128)
    url = models.URLField(verify_exists=False)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(Category, related_name='links')
    
    class Meta:
        ordering = ('title',)
    
    def __unicode__(self):
        return self.title