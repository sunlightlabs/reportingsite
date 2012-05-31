# -*- coding: utf-8 -*-

from django.db import models
from django.template.defaultfilters import slugify


class Organization(models.Model):
    name = models.CharField(max_length=255,
                            blank=False, 
                            null=False,
                            unique=True)
    
    slug = models.SlugField(max_length=255)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Organization, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'{0.name}'.format(self)


class Agency(models.Model):
    initials = models.CharField(max_length=10,
                                blank=False,
                                null=False,
                                unique=True)

    name = models.CharField(max_length=255,
                            blank=False,
                            null=False,
                            unique=True)

    slug = models.SlugField()

    meeting_list_url = models.TextField(blank=False, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Agency, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.initials)


class Attendee(models.Model):
    org = models.ForeignKey(Organization, related_name='representatives',
                            null=True)
    name = models.CharField(max_length=255, blank=False, null=False)

    def __unicode__(self):
        if self.org:
            return u'{0.name} from {0.org}'.format(self)
        else:
            return u'{0.name}'.format(self)


class Meeting(models.Model):
    import_hash = models.CharField(max_length=40,
                                   blank=False,
                                   null=False,
                                   unique=True)

    created = models.DateField(auto_now_add=True)

    agency = models.ForeignKey(Agency, related_name='meetings')
    date = models.DateField(null=False)
    communication_type = models.CharField(max_length=255,
                                          blank=True, 
                                          null=False)

    description = models.TextField(blank=True, null=False)

    """
    category and subcategory are just for the Fed while topic is used for
    all agencies. We include them all to generate a breadcrumb line.
    """
    category = models.TextField(null=False, blank=True)
    subcategory = models.TextField(null=False, blank=True)
    topic = models.TextField(null=False, blank=True)

    """
    Treasury specifies the organization that each attendee represents while
    the CTFC and FDIC specify only the organizations represented and the
    names of the attendees but does not specify which organization each
    attendee represents.
    """
    organizations = models.ManyToManyField(Organization, related_name='meetings')

    attendees = models.ManyToManyField(Attendee, related_name='meetings')

    """
    Since a meeting can be attended by multiple agency staff and multiple 
    visitors we put them all in the attendees table. This leaves the meeting
    table with too few columns to key by, so the scraperwiki scrapers generate
    an MD5 hash of the attendee names to distinguish otherwise identical meetings.
    """
    attendee_hash = models.CharField(max_length=40, blank=False, null=False)

    source_url = models.TextField(blank=False, null=False)

    def attendee_list(self):
        return Attendee.objects.filter(meeting=self)

    def __unicode__(self):
        return u'{0.pk}, {0.date!r}, {0.topic!r}, {0.attendee_hash!r}'.format(self)

    
