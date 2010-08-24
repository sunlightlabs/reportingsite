from django.db import models

class Committee(models.Model):
    id = models.CharField(max_length=9, primary_key=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    party = models.CharField(max_length=8)
    designation = models.CharField(max_length=1)
    treasurer = models.CharField(max_length=100)
    committee_designation = models.CharField(max_length=1)
    date_of_organization = models.DateField(null=True)

    def __unicode__(self):
        return self.name
