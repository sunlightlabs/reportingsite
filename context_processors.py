import datetime

from reporting.models import Post
from feedinator import Feed, FeedEntry
from buckley.models import Expenditure

from django.core.cache import cache

def latest_by_site(request):
    cache_key = 'latest_by_site'

    latest = cache.get(cache_key)
    if latest:
        return latest

    FLIT = Post.objects.filter(is_published=True, whichsite='FLIT')[:5]
    PT = FeedEntry.objects.filter(feed__codename='partytime')[:5]
    SS = Post.objects.filter(is_published=True, whichsite='SS')[:5]
    SLRG = Post.objects.filter(is_favorite=True, is_published=True, whichsite='SLRG')[:5]

    latest = {'FLIT': FLIT, 'SS': SS, 'PT': PT, 'SLRG': SLRG }
    cache.set(cache_key, latest, 60*60)

    return latest


def outside_spending_updated(request):
    expenditures = Expenditure.objects.order_by('-timestamp').values_list('timestamp', flat=True)
    if expenditures:
        updated = expenditures[0]
    else:
        updated = None
    return {'outside_spending_updated': updated - datetime.timedelta(hours=4), }
