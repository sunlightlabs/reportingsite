import json

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from tagging.models import TaggedItem
from tagging.utils import get_tag, get_tag_list
from tagging.views import tagged_object_list

from reportingsite.findatcat.models import Link, Category
from reportingsite.reporting.models import Post

def index(request):
    tag = "Finance Data Catalog"
    categories = Category.objects.all()
    return tagged_object_list(
        request,
        Post.objects.published().select_related(),
        tag,
        paginate_by=4,
        template_object_name='post',
        template_name='findatcat/index.html',
        extra_context={'tag': tag, 'categories': categories},
        allow_empty=True,
    )

def category(request, slug):

    category = Category.objects.get(slug=slug)

    # get posts: first published posts, then filter to findatcat tag,
    # then any matching category tag
    qs = Post.objects.published().select_related()
    qs = TaggedItem.objects.get_by_model(qs, get_tag('Finance Data Catalog'))
    posts = TaggedItem.objects.get_union_by_model(qs, get_tag_list(category.tag_list()))

    context = {
        'posts': posts,
        'links': category.links.all(),
        'current_category': category,
        'categories': Category.objects.all(),
    }

    return render_to_response('findatcat/category.html', context)

def filter(request):
    
    selected_categories = [int(c) for c in request.GET.get('cats', '').split(',') if c]
    links = Link.objects.filter(categories__id__in=selected_categories)

    if request.is_ajax() or 'json' in request.GET:
        def link2dict(link):
            return {
                'id': link.id,
                'title': link.title,
                'url': link.url,
                'description': link.description,
            }
        data = json.dumps([link2dict(l) for l in links])
        print data
        return HttpResponse(data, content_type='application/json')
    else:
        context = {
            'links': links,
            'selected_categories': selected_categories,
        }
        return render_to_response("findatcat/browse.html", context)