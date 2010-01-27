from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.syndication.feeds import Feed
from django.core.urlresolvers import reverse
from reporting.models import Post
from tagging.models import Tag, TaggedItem
from reporting.templatetags import lede

ITEMS_PER_FEED = getattr(settings, 'BLOGDOR_ITEMS_PER_FEED', 15)
FEED_TTL = getattr(settings, 'BLOGDOR_FEED_TTL', 20)

WHICHSITE_CHOICES = getattr(settings, "WHICHSITE_CHOICES", False)
#
# Generic blogdor feed
#

class BlogdorFeed(Feed):

    description_template = 'feeds/post_description.html'
    title_template = 'feeds/post_title.html'
   
    def link(self):
        return reverse('blogdor_archive')

    def ttl(self):
        return str(FEED_TTL)

    def item_description(self, post):
        return post.lede


#
# Specific blogdor feeds
#

class LatestPosts(BlogdorFeed):

    title = u"Sunlight Foundation Reporting Group"
    description = title
    
    def items(self):
        p = Post.objects.published()[:ITEMS_PER_FEED] 
        return p
        
    def item_title(self,post):
        return post.title.replace('&amp;','').replace('&#','')

    def item_author_name(self, post):
        if post.author:
            return post.author.get_full_name()
        return ""
    
    def item_pubdate(self, post):
        return post.date_published


class LatestFeatures(BlogdorFeed):

    title = u"Sunlight Foundation Reporting Group features"
    description = title
    
    def items(self):
        p = Post.objects.published().filter(is_favorite=True)[:ITEMS_PER_FEED] 
        return p
        
    def item_title(self,post):
        return post.title.replace('&amp;','').replace('&#','')

    def item_author_name(self, post):
        if post.author:
            return post.author.get_full_name()
        return ""
    
    def item_pubdate(self, post):
        return post.date_published


class LatestForAuthor(BlogdorFeed):

    feed_title = u"%s - Sunlight Foundation Reporting Group"
    feed_description = feed_title
    
    def _display_name(self, user):
        if hasattr(user, 'get_full_name'):
            display_name = user.get_full_name()
            if not display_name:
                display_name = user.username
            return display_name
        return user

    def title(self, author):
        return self.feed_title % self._display_name(author)

    def description(self, author):
        return self.feed_description % self._display_name(author)

    def item_pubdate(self, post):
        return post.date_published

    def get_object(self, bits):
        try:
            return User.objects.get(username=bits[-1])
        except User.DoesNotExist:
            return bits[-1]

    def items(self, author):
        return Post.objects.published().filter(author=author)[:ITEMS_PER_FEED]

class LatestForTag(BlogdorFeed):
    
    feed_title = u"'%s' - Sunlight Foundation Reporting Group"
    feed_description = feed_title
    
    def title(self, tag):
        return self.feed_title % tag
    
    def description(self, tag):
        return self.feed_description % tag
    
    def get_object(self, bits):
        try:
            return Tag.objects.get(name=bits[-1])
        except Tag.DoesNotExist:
            return bits[-1]

    def item_pubdate(self, post):
        return post.date_published

    def items(self, tag):
        if tag in [x[0] for x in WHICHSITE_CHOICES]:
            return Post.objects.published().filter(whichsite=tag)[:ITEMS_PER_FEED]
        return TaggedItem.objects.get_by_model(Post.objects.published(), tag)[:ITEMS_PER_FEED]



