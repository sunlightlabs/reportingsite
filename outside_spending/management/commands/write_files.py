import sys

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from django.core.management.base import BaseCommand, CommandError

from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, CSV_EXPORT_DIR

from outside_spending.views import all_expenditures_csv_to_file, all_contribs_csv_to_file


class Command(BaseCommand):
    help = "Dump the big files to a predefined spot in the filesystem. They need to then get moved to S3"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        b = conn.get_bucket('assets.sunlightfoundation.com')
        k = Key(b)
        
        print "Writing expenditures..."
        all_expenditures_csv_to_file()
        print "Writing contributions..."
        all_contribs_csv_to_file()

        
        for file_to_upload in ('all_contribs.csv', 'all_expenditures.csv'):
            print "pushing to S3: %s" % file_to_upload
            local_file_path = "%s/%s" % (CSV_EXPORT_DIR, file_to_upload)
            s3_string = "reporting/FTUM-data/%s" % file_to_upload
            k.key = s3_string
            k.set_contents_from_filename(local_file_path, policy='public-read')