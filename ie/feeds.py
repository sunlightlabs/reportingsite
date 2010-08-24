from django.contrib.syndication.views import Feed

from ie.models import Committee

class CommitteeFeed(Feed):
    title = "Newest independent expenditure committees"
    link = "/independent-expenditures/feed"
    description = "The latest independent expenditure committees to register with the FEC"

    def items(self):
        return Committee.objects.filter(date_of_organization__isnull=False).order_by('-date_of_organization')[:15]

    def item_link(self, item):
        return 'http://images.nictusa.com/cgi-bin/fecimg/?%s' % item.id

    def item_description(self, item):
        return "%s registered as an independent expenditure committee with the Federal Election Commission on %s." % (item.name, item.date_of_organization.strftime('%m/%d/%Y'))
