from django.template.defaultfilters import dictsortreversed
from feedinator.models import Feed, FeedEntry
from django.core.cache import cache
from django.views.decorators.cache import cache_page
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
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.views.generic import date_based, list_detail
from tagging.models import Tag
from tagging.views import tagged_object_list
from models import *
import datetime, time
from django.contrib.comments.models import Comment
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from haystack.query import SearchQuerySet

try:
    import json
except ImportError:
    import simplejson as json


POSTS_PER_PAGE = getattr(settings, "BLOGDOR_POSTS_PER_PAGE", 10)
YEAR_POST_LIST = getattr(settings, "BLOGDOR_YEAR_POST_LIST", False)
WP_PERMALINKS = False
WHICHSITE_CHOICES = getattr(settings, "WHICHSITE_CHOICES", False)


def post_detail(request, year, slug, month=None, day=None):
    key = 'reporting:%s:%s' % (year, slug)
    post = cache.get(key)
    if not post:
        post = get_object_or_404(Post, date_published__year=year, slug=slug, is_published=True)
        cache.set(key, post, 60*60)

    # Check whether the post is published. If so, show it.
    # If not, check whether the user requesting the page
    # is a staff member. Show unpublished posts only to staff.
    if not post.is_published and not request.user.is_staff:
        raise Http404

    return render_to_response('post_detail.html', 
                              {'post': post, 
                               'bodyclass': 'blog', },
                              context_instance=RequestContext(request))


#
# Post archive views
#
@cache_page(60 * 10)                  
def archive(request):
    return list_detail.object_list(
                    request,
                    queryset=Post.objects.published().select_related(),
                    paginate_by=POSTS_PER_PAGE,
                    template_name='posts_lede.html',
                    template_object_name='post',
                    allow_empty=True)

@cache_page(60 * 10)
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

@cache_page(60 * 10)
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

@cache_page(60*10)
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

@cache_page(60*10)
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


def admin_editing(request):
    if not request.user.is_staff:
        raise Http404
    uid = request.GET.get('uid', None)
    object_id = request.GET.get('objid', None)
    if not uid or not object_id:
        raise Http404

    user = get_object_or_404(User, id=uid)
    post = get_object_or_404(Post, id=object_id)

    user_editing_post, created = UserEditingPost.objects.get_or_create(user=user,
                                                                       post=post)
    if request.GET.get('closing', None) == '1':
        user_editing_post.delete()
        return HttpResponse('')

    user_editing_post.save() # To update timestamp

    other_users_editing = UserEditingPost.objects.exclude(user=user).filter(post=post)
    if other_users_editing:
        users = [editor.user.username for editor in other_users_editing]
        return HttpResponse(json.dumps(users))

    return HttpResponse('[]')

#
# Author views
#

@cache_page(60 * 10)
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


def mergetweets(posts, tweetsfeed, ptentries):
    elist = []
    for p in posts:
        elist.append(p) 
    for p in ptentries:
        elist.append(p) 
    for t in tweetsfeed:
        elist.append({ 'date_published': t.date_published, 'byline': '', 'text': t.title[t.title.find(': ')+2:], 'twit': t.title[:t.title.find(': ')] })
    elist = dictsortreversed(elist, 'date_published')
    return elist


def index(request):

    key = 'reporting_featured_posts'
    featured = cache.get(key)
    if not featured:
        featured = Post.objects.favorites().select_related()[:4]
        cache.set(key, featured, 60*60)

    #key = 'reporting_homepage_bloglist'
    #blogs = cache.get(key)
    #if not blogs:
    blogs = mergetweets(
                Post.objects.published().filter(is_favorite=False).select_related()[:10],
                FeedEntry.objects.filter(feed__codename__startswith='tweetsRT-').select_related()[:4],
                Feed.objects.get(codename='partytime').entries.all().select_related()[:15])
    #    cache.set(key, blogs, 60*15)

    from buckley.views import widget
    ie_data, last_update = widget()


    return render_to_response('index.html', 
                              {'blogs': blogs, 'featured': featured, 'bodyclass': 'home',
                               'host': request.META['HTTP_HOST'],
                               'ies': ie_data,
                               'last_ie_update': last_update,
                              },
                              context_instance=RequestContext(request))


@cache_page(60 * 10)
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


def search(request):
    results = None
    page = None
    query = request.GET.get('q')
    order = request.GET.get('order', 'date')

    if query:
        if order == 'rel': # Sort by relevance
            results = SearchQuerySet().filter(content=query)
        else: # Default: sort by date
            order = 'date'
            results = SearchQuerySet().filter(content=query).order_by('-date_published')

        paginator = Paginator(results, 20, orphans=5)

        pagenum = request.GET.get('page', 1)
        try:
            page = paginator.page(pagenum)
        except (EmptyPage, InvalidPage):
            raise Http404

    return list_detail.object_list(request,
                                   queryset=Post.objects.all(),
                                   paginate_by=20,
                                   template_name='search/search.html',
                                   template_object_name='posts',
                                   allow_empty=True,
                                   extra_context={'query': query,
                                                  'page': page,
                                                  'results': results, # So we can access things like results.count()
                                                  'order': order,
                                                  'hide_sidebar_search': True,
                                                 }
                                   )


def adminfiles(request):
    uploads = Upload.objects.all().order_by('-pk')  
    return render_to_response('uploads.html', {'uploads': uploads})

@cache_page(60 * 60)
def handler404(request):
    return archive(request)
