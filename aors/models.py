from django.db import models

class AORDocument(models.Model):
    aor_description = models.CharField(max_length=255)
    aor_id = models.IntegerField()
    aor_number = models.CharField(max_length=10)
    org = models.CharField(max_length=255)
    doc_url = models.URLField(verify_exists=False, unique=True)
    doc_description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'timestamp'
        ordering = ['-timestamp', '-doc_url', ]

    def __unicode__(self):
        return '%s: %s' % (self.aor_description, self.doc_description, )
