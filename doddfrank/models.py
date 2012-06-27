# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
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
        self.slug = slugify(self.initials)
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

    class Meta:
        unique_together = ('name', 'org')


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

    def visitor_list(self):
        return self.attendees.exclude(org__name__icontains=self.agency.name)

    def __unicode__(self):
        return u'{0.pk}, {0.date!r}, {0.topic!r}, {0.attendee_hash!r}'.format(self)


class OrganizationNameCorrection(models.Model):
    """
    We maintain a mapping of name replacements to avoid re-importing mis-spellings.
    """

    original = models.CharField(max_length=255,
                                blank=False, 
                                null=False,
                                unique=True)

    replacement = models.CharField(max_length=255,
                                   blank=False, 
                                   null=False)

    def encoded_original(self):
        return repr(self.original.encode('utf-8'))

    def encoded_replacement(self):
        return repr(self.replacement.encode('utf-8'))

    def __unicode__(self):
        return u'{0.original} => {0.replacement}'.format(self)

    def clean(self):
        corrections = OrganizationNameCorrection.objects.filter(
            Q(original=self.replacement) | Q(replacement=self.original))
        if corrections.count() > 0:
            raise ValidationError("Correction loop detected {0!r}".format(list(corrections)))

    def save(self, *args, **kwargs):
        super(OrganizationNameCorrection, self).save(*args, **kwargs)

        # If there is no existing organization, then there's nothing to
        # correct right now and this is just being created for future use.
        try:
            original_org = Organization.objects.get(name=self.original)
        except Organization.DoesNotExist:
            return

        try:
            replacement_org = Organization.objects.get(name=self.replacement)
            # If an organization already exists with the replacement name then 
            # the correction needs to be done on the Meeting and Organization
            # objects.
            for meeting in original_org.meetings.all():
                meeting.organizations.remove(original_org)
                meeting.organizations.add(replacement_org)
                meeting.save()

            for attendee in original_org.representatives.all():
                try:
                    doppleganger = Attendee.objects.get(name=attendee.name, org=replacement_org)
                    for meeting in attendee.meetings.all():
                        doppleganger.meetings.add(meeting)
                    attendee.delete()
                except Attendee.DoesNotExist:
                    attendee.org = replacement_org
                    attendee.save()

            original_org.delete()

        except Organization.DoesNotExist:
            # If there isn't already an Organization object with the replacement
            # name then there are no Meeting or Attendee objects to update and we
            # can just rename the original Organization object.
            original_org.name = self.replacement
            original_org.save()


class ScrapingError(models.Model):
    agency = models.ForeignKey(Agency, related_name='scraping_errors')
    url = models.TextField(null=False, blank=False)
    description = models.TextField(null=True)
    context = models.TextField(null=True)
    timestamp = models.DateTimeField(null=True)

