from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from tagging.fields import TagField
import datetime
from django.contrib.sites.models import Site

from comments import BlogdorModerator
from django.contrib.comments.moderation import moderator

from django.template.loader import render_to_string


COMMENT_FILTERS = getattr(settings, "BLOGDOR_COMMENT_FILTERS", [])
WP_PERMALINKS = getattr(settings, "BLOGDOR_WP_PERMALINKS", False)
WHICHSITE_CHOICES = getattr(settings, "WHICHSITE_CHOICES", False)

class PostQuerySet(models.query.QuerySet):
    
    def publish(self):
        now = datetime.datetime.now()
        count = self.filter(date_published__isnull=False).update(is_published=True)
        count += self.filter(date_published__isnull=True).update(is_published=True, date_published=now)
        return count
        
    def recall(self):
        return self.update(is_published=False)

class PostManager(models.Manager):
    
    use_for_related_fields = True
    
    def published(self):
        return Post.objects.filter(is_published=True)
        
    def get_query_set(self):
        return PostQuerySet(self.model)

class Post(models.Model):
    objects = PostManager()
   
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=64, db_index=True)
    author = models.ForeignKey(User, related_name='posts')
    
    content = models.TextField() 
    excerpt = models.TextField(blank=True)  
    
    timestamp = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    
    date_published = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    
    is_favorite = models.BooleanField(default=False)
    
    comments_enabled = models.BooleanField(default=True)
    
    tags = TagField()

    whichsite = models.CharField(max_length=10, choices=WHICHSITE_CHOICES)

    pullquote = models.CharField(max_length=255, blank=True)
    override_byline = models.CharField(max_length=255, blank=True)

    image = models.FileField(upload_to='images', max_length=500)


    def shortbyline(self):
        if self.override_byline:
            return "By " + self.override_byline
        return 'By <a href="/author/' + self.author.username + '">' + self.author.first_name + " " + self.author.last_name + '</a>'


 
    class Meta:
        ordering = ['-date_published','-timestamp']
        
    def __unicode__(self):
        return self.title
    
    @models.permalink
    def get_absolute_url(self):        
        params = {
            'year': self.date_published.year,
            'slug': self.slug,
        }
        urlname = 'blogdor_post'
        if WP_PERMALINKS:
            urlname += '_wpcompat'
            params['month'] = "%02d" % self.date_published.month,
            params['day'] = "%02d" % self.date_published.day
        return (urlname, (), params)
        
    def publish(self):        
        self.is_published = True
        self.save()
    
    def recall(self):
        self.is_published = False
        self.save()




moderator.register(Post, BlogdorModerator)


class CurrentEdit(models.Model):
    post = models.ForeignKey(Post)
    user = models.ForeignKey(User)
    time = models.IntegerField()




