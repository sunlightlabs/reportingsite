from feedinator.models import Feed, FeedEntry
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from icalendar import Calendar, Event, vDatetime
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
from models import Post
import datetime, time
from django.contrib.comments.models import Comment

POSTS_PER_PAGE = getattr(settings, "BLOGDOR_POSTS_PER_PAGE", 10)
YEAR_POST_LIST = getattr(settings, "BLOGDOR_YEAR_POST_LIST", False)
WP_PERMALINKS = False

                            
def post(request, year, slug):
    return _post(request, year, slug)

def post_wpcompat(request, year, month, day, slug):
        post = get_object_or_404(Post, date_published__year=year, date_published__month=month, slug__startswith=slug[:60], is_published=True)
        return  _post_by_id(request, post.id)

def _post(request, year, slug):
    post = Post.objects.get(date_published__year=year, slug=slug, is_published=True)
    return _post_by_id(request, post.id)

def _post_by_id(request, id):
    post = Post.objects.get(pk=id)
    ourposts = Post.objects.published().exclude(pk=post.id)[:4]

    from django.template.loader import render_to_string
    resources = FeedEntry.objects.filter(feed__codename__startswith='Resource-')[:7]
    news = Feed.objects.filter(codename__startswith='News-')  

    def getcal():      
        cal = FeedEntry.objects.filter(feed__codename__startswith='Calendar-')  
        cl = []
        today = datetime.datetime.now().date()
        for e in cal:
            d = e.summary[10:22]
            t = time.strptime(d, "%b %d, %Y")
            t = datetime.date.fromtimestamp(time.mktime(t))
            if t>=today:
                cl.append({'date': t, 'summary': e.title })
        cl = sorted(cl, key=itemgetter('date'))
        for c in cl:
            c['date'] = str(c['date'])[5:]
        return cl[:2]

    calendars = getcal()
    comments = Comment.objects.for_model(Post).filter(is_public=True).order_by('-submit_date')[:2]
    side = render_to_string('feedbar.html',  {'resources': resources, 'news': news, 'calendars': calendars, 'ourposts': ourposts, 'comments': comments })


    return render_to_response('post_detail.html', {'post': post, 'sidebar': side })

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
                    allow_empty=True)

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


#
# Author views
#

def author(request, username):
    try:
        author = User.objects.get(username=username)
        return list_detail.object_list(
                    request,
                    queryset=Post.objects.published().select_related().filter(author=author),
                    paginate_by=POSTS_PER_PAGE,
                    template_object_name='post',
                    template_name='posts_lede.html',
                    extra_context={'author':author},
                    allow_empty=True)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('blogdor_archive'))

#
# Preview view
#

def preview(request, post_id, slug):
    try:
        post = Post.objects.select_related().get(pk=post_id, slug=slug)
        if post.is_published:
            return HttpResponsePermanentRedirect(post.get_absolute_url())
        else:
            return list_detail.object_detail(
                    request,
                    queryset=Post.objects.select_related().all(),
                    object_id=post_id,
                    template_object_name='post')
    except Post.DoesNotExist:
        return HttpResponseRedirect(reverse('blogdor_archive'))


def index(request):
   
    def mergetweets(posts, tweetsfeed):
        elist = []
        for p in posts:
            elist.append({ 'title': '<a href="'+p.get_absolute_url()+'">'+p.title+'</a>', 'date': p.date_published, 'byline': p.author, 'text': p.lede() })
        for t in tweetsfeed.entries.all()[:7]:
            elist.append({ 'title': '', 'date': t.date_published, 'byline': '', 'text': t.title[t.title.find(': ')+2:]})
        elist = sorted(elist, key=itemgetter('date'))
        elist.reverse()
        for e in elist:
            day = e['date'].strftime("%m/%d/%y")
            now = datetime.datetime.now().strftime("%m/%d/%y")
            if day==now:
                e['date']= e['date'].strftime("%H:%m%P")
                if e['date'][:1]=='0':
                    e['date'] = e['date'][1:]
            else:
                e['date']=''
        return elist

    featured = Post.objects.published().filter(is_favorite=True)[0:2] 
    f1 = featured[0].pk
    f2 = featured[1].pk
    stories = Post.objects.exclude(pk=f1).exclude(pk=f2).filter(blogreport='R', is_published=True)[0:7] 
    blogs = mergetweets( Post.objects.filter(blogreport='B', is_published=True)[0:7], Feed.objects.get(codename__startswith='tweetsRT-')  )[0:7]

    FLIT = Post.objects.filter(is_published=True, whichsite='FLIT')[0:5] 
    PT = Feed.objects.get(codename='partytime').entries.all()[:3]
    SS = Post.objects.filter(is_published=True, whichsite='SS')[0:5] 
    SLRG = Post.objects.filter(blogreport='R', is_published=True, whichsite='SLRG')[0:5] 

    return render_to_response('index.html', {'blogs': blogs, 'stories': stories, 'featured': featured, 'FLIT': FLIT, 'SS': SS, 'PT': PT, 'SLRG': SLRG })



def feedbar(request):
    ourposts = Post.objects.published()[:6]
    resources = FeedEntry.objects.filter(feed__codename__startswith='Resource-')[:12]
    news = Feed.objects.filter(codename__startswith='News-')  

    def getcal():      
        cal = FeedEntry.objects.filter(feed__codename__startswith='Calendar-')  
        cl = []
        today = datetime.datetime.now().date()
        for e in cal:
            d = e.summary[10:22]
            t = time.strptime(d, "%b %d, %Y")
            t = datetime.date.fromtimestamp(time.mktime(t))
            if t>=today:
                cl.append({'date': t, 'summary': e.title })
        cl = sorted(cl, key=itemgetter('date'))
        for c in cl:
            c['date'] = str(c['date'])[5:]
        return cl[:4]

    calendars = getcal()
    comments = Comment.objects.for_model(Post).filter(is_public=True).order_by('-submit_date')[:2]
    return render_to_response('feedbar.html',  {'resources': resources, 'news': news, 'calendars': calendars, 'ourposts': ourposts, 'comments': comments })


def realtime(request):
    stories = Post.objects.filter(is_published=True, blogreport='B')   

    paginator = Paginator(stories, 25) # Show 25 contacts per page
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    # If page request (9999) is out of range, deliver last page of results.
    try:
        stories = paginator.page(page)
    except (EmptyPage, InvalidPage):
        stories = paginator.page(paginator.num_pages)

    return render_to_response('posts_full.html', {'page_obj': stories })



def stories(request):
    stories = Post.objects.filter(is_published=True, blogreport='R')   

    paginator = Paginator(stories, 25) # Show 25 contacts per page
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    # If page request (9999) is out of range, deliver last page of results.
    try:
        stories = paginator.page(page)
    except (EmptyPage, InvalidPage):
        stories = paginator.page(paginator.num_pages)

    return render_to_response('posts_lede.html', {'page_obj': stories })



def bysite(request, site):
    stories = Post.objects.published().filter(whichsite=site)   

    paginator = Paginator(stories, 25) # Show 25 contacts per page
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    # If page request (9999) is out of range, deliver last page of results.
    try:
        stories = paginator.page(page)
    except (EmptyPage, InvalidPage):
        stories = paginator.page(paginator.num_pages)

    if site=='FLIT':
        return render_to_response('flit.html', {'page_obj': stories })
    if site=='SS':
        return render_to_response('ss.html', {'page_obj': stories })

    return render_to_response('posts_lede.html', {'page_obj': stories })


def search(request):

    if request.GET['terms']:
        terms = request.GET['terms']
    else:
        return HttpResponseRedirect(reverse('blogdor_archive'))

    stories = Post.objects.published().filter(Q(title__icontains=terms) | Q(content__icontains=terms)) #change to __search on mysql  

    paginator = Paginator(stories, 25) # Show 25 contacts per page
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    # If page request (9999) is out of range, deliver last page of results.
    try:
        stories = paginator.page(page)
    except (EmptyPage, InvalidPage):
        stories = paginator.page(paginator.num_pages)

    return render_to_response('posts_lede.html', {'page_obj': stories })
