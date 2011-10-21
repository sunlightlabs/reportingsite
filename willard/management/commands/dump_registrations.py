from cStringIO import StringIO
import csv
import sys
import hashlib
import base64

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from django.core.management.base import BaseCommand
from django.conf import settings

from willard.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        output = StringIO()
        csv.writer(output).writerow(['id',
                                         'registration_type',
                                         'registrant',
                                         'client',
                                         'received',
                                         'issues',
                                         'specific_issue', ])
        for registration in Registration.objects.all():
            csv.writer(output).writerow(registration.as_csv())


        bucket_name = 'assets.sunlightfoundation.com'
        connection = S3Connection(settings.MEDIASYNC.get('AWS_KEY'), settings.MEDIASYNC.get('AWS_SECRET'))

        headers = {
            "x-amz-acl": "public-read",
            "Content-Type": 'text/csv',
        }

        #filedata = open(filepath, 'r').read()
        filedata = output.getvalue()

        # calculate md5 digest of filedata
        checksum = hashlib.md5(filedata)
        hexdigest = checksum.hexdigest()
        b64digest = base64.b64encode(checksum.digest())

        bucket = connection.get_bucket(bucket_name)
        key = Key(bucket)
        key.key = '/reporting/uploads/%s' % 'lobbyist_registrations.csv'
        key.set_contents_from_string(filedata, headers=headers, md5=(hexdigest, b64digest))

        print key.generate_url(60*60*24*8).split('?')[0].replace('https', 'http')
