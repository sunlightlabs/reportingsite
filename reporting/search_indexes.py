from haystack import site
from haystack.indexes import *

from reporting.models import Post


class PostIndex(RealTimeSearchIndex):
    title = CharField()
    content = CharField(document=True, use_template=True)
    date_published = DateField(model_attr='date_published')

    def get_queryset(self):
        return Post.objects.published() | Post.objects.filter(is_published=True, show_on_index_pages=False)


site.register(Post, PostIndex)
