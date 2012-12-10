from haystack import indexes

from reporting.models import Post


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    title = indexes.CharField()
    text = indexes.CharField(document=True, use_template=True)
    date_published = indexes.DateField(model_attr='date_published')

    def get_queryset(self):
        return Post.objects.published() | Post.objects.filter(is_published=True, show_on_index_pages=False)
        
    def get_model(self):
        return Post


    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()


#site.register(Post, PostIndex)
