from feedinator.models import Feed, FeedEntry
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q
import urllib
import datetime
from operator import itemgetter
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import *
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import date_based, list_detail
from tagging.models import Tag
from tagging.views import tagged_object_list
from models import *
import datetime, time
from django.contrib.comments.models import Comment
from django.template import RequestContext

POSTS_PER_PAGE = getattr(settings, "BLOGDOR_POSTS_PER_PAGE", 10)
YEAR_POST_LIST = getattr(settings, "BLOGDOR_YEAR_POST_LIST", False)
WP_PERMALINKS = False
WHICHSITE_CHOICES = getattr(settings, "WHICHSITE_CHOICES", False)
                            
def post(request, year, slug):
    return _post(request, year, slug)

def post_wpcompat(request, year, month, day, slug):
    post = get_object_or_404(Post, date_published__year=year, date_published__month=month, slug__startswith=slug[:56], is_published=True)
    return  _post_by_id(request, post.id)

def _post(request, year, slug):
    post = get_object_or_404(Post, date_published__year=year, slug=slug, is_published=True)
    return _post_by_id(request, post.id)

def _post_by_id(request, id):
    post = get_object_or_404(Post, pk=id)

    return render_to_response('post_detail.html', {'post': post, 'bodyclass': 'blog'   }, context_instance=RequestContext(request))


#
# Preview view
#
def preview(request, object_id):
    from django.contrib.auth.decorators import login_required
    login_required(preview)
    try:
        post = Post.objects.get(pk=object_id)
        if post.is_published:
            return HttpResponsePermanentRedirect(post.get_absolute_url())
        else:
            return render_to_response('post_detail.html', {'post': post, 'bodyclass': 'blog'   }, context_instance=RequestContext(request))
    except Post.DoesNotExist:
        return HttpResponseRedirect(reverse('blogdor_archive'))



#
# Post archive views
#
                  
def archive(request):
    return list_detail.object_list(
                    request,
                    queryset=Post.objects.published().select_related(),
                    paginate_by=POSTS_PER_PAGE,
                    template_name='posts_lede.html',
                    template_object_name='post',
                    allow_empty=True)

def archive_month(request, year, month):
    return date_based.archive_month(
                    request,
                    queryset=Post.objects.published().select_related(),
                    date_field='date_published',
                    year=year,
                    month=month,
                    month_format="%m",
                    template_name='post_archive_month.html',
                    template_object_name='post',
                    allow_empty=False)

def archive_year(request, year):
    return date_based.archive_year(
                    request,
                    queryset=Post.objects.published().select_related(),
                    date_field='date_published',
                    year=year,
                    template_object_name='post',
                    template_name='post_archive_year.html',
                    make_object_list=YEAR_POST_LIST,
                    allow_empty=True)

#
# Post tag views
#

def tag(request, tag):
    return tagged_object_list(
                    request,
                    Post.objects.published().select_related(),
                    tag,
                    paginate_by=POSTS_PER_PAGE,
                    template_object_name='post',
                    template_name='posts_lede.html',
                    extra_context={'tag': tag},
                    allow_empty=True)

def tag_list(request):
    ct = ContentType.objects.get_for_model(Post)
    return list_detail.object_list(
                    request,
                    queryset=Tag.objects.filter(items__content_type=ct),
                    paginate_by=POSTS_PER_PAGE,
                    template_name='tag_list.html',
                    template_object_name='tag',
                    allow_empty=True)

def tag_list_admin(request):
    ct = ContentType.objects.get_for_model(Post)
    return list_detail.object_list(
                    request,
                    queryset=Tag.objects.filter(items__content_type=ct),
                    paginate_by=POSTS_PER_PAGE,
                    template_name='tag_list_admin.html',
                    template_object_name='tag',
                    allow_empty=True)

def admin_currentedit(request, user_id, post_id):
    from django.contrib.auth.decorators import login_required
    from time import time

    login_required(admin_currentedit)

    t = time()
    twominago = t-150
    u = User.objects.get(id=user_id)
    p = Post.objects.get(id=post_id)
    #c = request.POST['content']
    deleteyou = Backup.objects.filter(post=p,user=u).delete()
    check = Backup.objects.filter(post=p,time__gt=twominago)
    listusers = []
    for c in check:
        listusers.append( c.user.username )
    Backup(post=p,user=u,time=t).save()
    if len(listusers)>0:
         s = "Also editing: " + ", ".join(listusers)
    else:
        s=''
    return HttpResponse(s )


#
# Author views
#

def author(request, username):
    try:
        author = User.objects.get(username=username)
        topinfo = 'Investigations by Sunlight Foundation reporter <a href="http://sunlightfoundation.com/people/'+username+'">' + author.first_name + ' ' + author.last_name + '</a>'
        return list_detail.object_list(
                    request,
                    queryset=Post.objects.published().select_related().filter(author=author),
                    paginate_by=POSTS_PER_PAGE,
                    template_object_name='post',
                    template_name='posts_lede.html',
                    extra_context={'author':author, 'topinfo': topinfo},
                    allow_empty=True)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('blogdor_archive'))



def index(request):
   
    def mergetweets(posts, tweetsfeed, ptentries):
        elist = []
        for p in posts:
            elist.append(p) 
        for p in ptentries.entries.all():
            elist.append(p) 
        for t in tweetsfeed:
            elist.append({ 'date_published': t.date_published, 'byline': '', 'text': t.title[t.title.find(': ')+2:], 'twit': t.title[:t.title.find(': ')] })
        return elist

    featured = Post.objects.published().filter(is_favorite=True)[:4] 
    f1 = featured[0].pk
    f2 = featured[1].pk
    f3 = featured[2].pk
    f4 = featured[3].pk
    blogs = mergetweets( Post.objects.published().exclude(pk=f1).exclude(pk=f2).exclude(pk=f3).exclude(pk=f4), FeedEntry.objects.filter(feed__codename__startswith='tweetsRT-')[:3], Feed.objects.get(codename='partytime')  )

    return render_to_response('index.html', {'blogs': blogs, 'featured': featured, 'bodyclass': 'home' }, context_instance=RequestContext(request) )
    """def mergetweets(posts, ptentries):
        elist = []
        for p in posts:
            elist.append(p) 
        for p in ptentries.entries.all():
            elist.append(p) 
        for t in tweetsfeed:
            elist.append({ 'date_published': t.date_published, 'byline': '', 'text': t.title[t.title.find(': ')+2:], 'twit': t.title[:t.title.find(': ')] })
        return elist

    featured = Post.objects.published().filter(is_favorite=True)[:4] 
    f1 = featured[0].pk
    f2 = featured[1].pk
    f3 = featured[2].pk
    f4 = featured[3].pk
    blogs = mergetweets( Post.objects.published().exclude(pk=f1).exclude(pk=f2).exclude(pk=f3).exclude(pk=f4), Feed.objects.get(codename='partytime')  )
    tweets = FeedEntry.objects.filter(feed__codename__startswith='tweetsRT-')
    return render_to_response('index.html', {'blogs': blogs, 'featured': featured, 'bodyclass': 'home', 'tweets': tweets }, context_instance=RequestContext(request) )"""



def bysite(request, site):
    topinfo=''
    if site=='features':
        stories = Post.objects.published().filter(is_favorite=True)   
    else:
        stories = Post.objects.published().filter(whichsite=site)  

    if site=='FLIT':
        t='flit.html'
    elif site=='SS':
        t='ss.html'
    else:
        t='posts_lede.html'

    return list_detail.object_list(request,
                    queryset=stories,
                    paginate_by=POSTS_PER_PAGE,
                    template_name=t,
                    template_object_name='post', allow_empty=True,
                    extra_context={'topinfo': topinfo},
                    )


def searchredirect(request):

    if request.GET['terms']:
        terms = request.GET['terms']
        return HttpResponseRedirect('/search/'+terms)
    else:
        return HttpResponseRedirect(reverse('blogdor_archive'))

  
def search(request, terms):

    stories = Post.objects.published().filter(Q(title__icontains=terms) | Q(content__icontains=terms)) #change to __search on mysql  

    return list_detail.object_list(request,
                    queryset=stories,
                    paginate_by=POSTS_PER_PAGE,
                    template_name='posts_lede.html',
                    template_object_name='post', allow_empty=True
                    )


def handler404(request):
    return archive(request)

