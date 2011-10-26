from django.conf import settings
from django.http import HttpResponse
from tagging.views import tagged_object_list

from reportingsite.reporting.models import Post

def index(request):
    tag = "Finance Data Catalog"
    #return HttpResponse(tag)
    return tagged_object_list(
        request,
        Post.objects.published().select_related(),
        tag,
        paginate_by=getattr(settings, 'POSTS_PER_PAGE', 10),
        template_object_name='post',
        template_name='findatcat/index.html',
        extra_context={'tag': tag},
        allow_empty=True,
    )