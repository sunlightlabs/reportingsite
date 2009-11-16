from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from markupfield.fields import MarkupField
from tagging.fields import TagField
import datetime
from django.contrib.sites.models import Site

from comments import BlogdorModerator
from django.contrib.comments.moderation import moderator

COMMENT_FILTERS = getattr(settings, "BLOGDOR_COMMENT_FILTERS", [])
WP_PERMALINKS = getattr(settings, "BLOGDOR_WP_PERMALINKS", False)
DEFAULT_MARKUP = getattr(settings, "BLOGDOR_DEFAULT_MARKUP", "markdown")


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
    excerpt = models.TextField()  
    
    timestamp = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)
    
    date_published = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    
    is_favorite = models.BooleanField(default=False)
    
    comments_enabled = models.BooleanField(default=True)
    
    tags = TagField()

    whichsite = models.CharField(max_length=10, choices=(('SLRG', 'Sunlight Reporting Group'), ('SS', 'SubsidyScope'), ('FLIT', 'FLIT')))
    blogreport = models.CharField(max_length=10, choices=(('B', 'Blog'), ('R','Report')))

    pullquote = models.CharField(max_length=255, blank=True)


    def byline(self):
        import time, datetime
        d1 = self.date_published.strftime("%h %d")
        d2 = self.date_published.strftime("%I:%M%P")
        if d2[0:1]=='0':
            d2 = d2[1:]
        d = d1 + " " + d2      
        return "By " + self.author.first_name + " " + self.author.last_name + " " + d

    def lede(self): 
        from django.utils.html import strip_tags 

        if self.excerpt.strip()!='' and self.excerpt.strip()!=None and self.excerpt!='<br>':
            return strip_tags(self.excerpt)
        if len(self.content)<200:
            return strip_tags(self.content)  

        readmore = ' <a href="'+self.get_absolute_url()+'">(Read all about it...)</a>'
  
        grafs = self.content.strip().split('\n')
        if grafs[0].strip()!='' and  grafs[0].strip()!=None:
            lede = grafs[0]
        else: 
            lede = grafs[1]
        if len(lede)<300:
            return strip_tags(lede) + readmore
        else:
            sentences = lede.split('. ')
            if len(sentences[0])>400:
                return strip_tags(sentences[0][:400]) + readmore
            i=0
            lede = sentences[0]
            while len(sentences)>i+1 and len(lede)<400:
                i = i+1
                lede = lede + ". " + sentences[i]
            return strip_tags(lede) + readmore

  
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




