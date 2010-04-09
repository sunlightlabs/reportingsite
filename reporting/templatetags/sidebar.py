from django.template import Library, Node
import re
from reporting.models import *
from feedinator import Feed, FeedEntry

register = Library()


class OutsideArticles(Node):
    def render(self, context):
        context['entries'] = FeedEntry.objects.filter(feed__codename__startswith='News-').select_related()[:8]
        return ''
    
def get_outside_articles(parser, token):
    return OutsideArticles()
get_outside_articles = register.tag(get_outside_articles)


class OurPosts(Node):
    def __init__(self, exclude=None):
        self.exclude = exclude
    def render(self, context):
        if self.exclude:
            context['ourposts'] = Post.objects.published().exclude(pk=context[self.exclude].pk)[:6]
        else:
            context['ourposts'] = Post.objects.published()[:6]
        return ''
    
def get_ourposts(parser, token):
    bits = token.contents.split()
    exclude = None
    if len(bits)>1:
        exclude = bits[1]
    return OurPosts(exclude)
get_ourposts = register.tag(get_ourposts)



class Calendar(Node):
    def render(self, context):    
        import time, datetime
        from operator import itemgetter 
        cal = FeedEntry.objects.filter(feed__codename__startswith='Calendar-').select_related()
        cl = []
        today = datetime.datetime.now().date()
        for e in cal:
            da = e.summary.split()
            d = da[2] + ' ' + da[3] + ' ' + da[4][:4]
            t = time.strptime(d, "%b %d, %Y")
            t = datetime.date.fromtimestamp(time.mktime(t))
            if t>=today:
                cl.append({'date': t, 'summary': e.title })
        cl = sorted(cl, key=itemgetter('date'))        
        context['events'] = cl
        return ''

def get_calendar(parser, token):
    return Calendar()
get_calendar = register.tag(get_calendar)

    

class ResourceFeed(Node):
    def render(self, context):
        f = FeedEntry.objects.filter(feed__codename__startswith='Resource-').select_related()[:10]
        usedfeed = []        
        l = []
        for ff in f:
            if ff.feed.title not in usedfeed:
                usedfeed.append(ff.feed.title)
                l.append(ff)
                if len(l)>=10:
                    break 
        context['entries'] = l        
        return ''
    
def get_resources(parser, token):
    return ResourceFeed()
get_resources = register.tag(get_resources)


