from reporting.models import Post
from feedinator import Feed
 
def latest_by_site(request):
    FLIT = Post.objects.filter(is_published=True, whichsite='FLIT')[:5] 
    PT = Feed.objects.get(codename='partytime').entries.all()[:5]
    SS = Post.objects.filter(is_published=True, whichsite='SS')[:5] 
    SLRG = Post.objects.filter(blogreport='R', is_published=True, whichsite='SLRG')[:5] 

    return {'FLIT': FLIT, 'SS': SS, 'PT': PT, 'SLRG': SLRG }

