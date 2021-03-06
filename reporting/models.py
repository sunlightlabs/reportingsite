import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.comments.moderation import moderator
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import signals
from django.template.loader import render_to_string
from tagging.fields import TagField
import tagging

from reporting.comments import BlogdorModerator

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
        return Post.objects.filter(is_published=True, show_on_index_pages=True)

    def favorites(self):
        return Post.objects.filter(is_published=True, is_favorite=True, show_on_index_pages=True)
        
    def get_query_set(self):
        return PostQuerySet(self.model)



class Post(models.Model):
    objects = PostManager()
   
    title = models.CharField('Headline', max_length=255)
    slug = models.SlugField(max_length=64, db_index=True)
    author = models.ForeignKey(User, related_name='posts')
    
    content = models.TextField() 
    excerpt = models.TextField(blank=True)  
    
    timestamp = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    
    date_published = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    
    is_favorite = models.BooleanField( default=False)
    is_featured = models.BooleanField(default=False)
    
    comments_enabled = models.BooleanField(default=True)
    
    tags = TagField()

    whichsite = models.CharField(max_length=10, choices=WHICHSITE_CHOICES)

    pullquote = models.CharField(max_length=255, blank=True)
    override_byline = models.CharField("Override byline (for special contributor or multiple writers)", max_length=255, blank=True)

    image = models.FileField(upload_to='images', max_length=500)

    show_on_index_pages = models.BooleanField(default=True)

    users_editing = models.ManyToManyField(User, through='UserEditingPost')
    fb_image_url = models.CharField(help_text="Suggest an image for facebook to use in sharing the post; note that this doesn't guarantee that facebook will actually use it. Both height and width must be greater than 200px; the aspect ratio can't be more than 3:1.", max_length=512, null=True, blank=True)


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

    def days_old(self):
        return (datetime.datetime.now() - self.date_published).days
        
    def date_published_gmt(self):
        # hack to return an approximate gmt time.
        return(self.date_published  +  datetime.timedelta(hours=5) )


def cache_updater(sender, **kwargs):
    instance = kwargs['instance']
    key = 'reporting:%s:%s' % (instance.date_published.year, instance.slug)
    cache.set(key, instance, 60*60)
    cache.delete('reporting_featured_posts')


def cache_deleter(sender, **kwargs):
    instance = kwargs['instance']
    key = 'reporting:%s:%s' % (instance.date_published.year, instance.slug)
    cache.delete(key)

    if instance.is_favorite:
        cache.delete('reporting_featured_posts')


signals.post_save.connect(cache_updater, sender=Post)
signals.pre_delete.connect(cache_deleter, sender=Post)

#moderator.register(Post, BlogdorModerator)

# try:
#     tagging.register(Post)
# except tagging.AlreadyRegistered:
#     pass


class UserEditingPost(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user', 'post'), )



class Backup(models.Model):
    post = models.ForeignKey(Post)
    user = models.ForeignKey(User)
    time = models.IntegerField()
  


from django.core.files.base import ContentFile
from django.core.files.storage import default_storage as s3_storage
from django.core.cache import cache
#from storages.backends.s3 import *

class Upload(models.Model):
    myfile = models.FileField(storage=s3_storage, upload_to='uploads')
    name = models.CharField(max_length=50)

    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return self.myfile._name

    def link(self):
        return self.myfile.storage.url('')[:-1] + self.myfile.file._name
    def short(self):
        f = self.myfile.file._name
        fs = f.split('/')
        if(len(fs)>1):
            return fs[1]
        else:
            return f


