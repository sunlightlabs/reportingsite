# This is set to run as a python script outside of django. 

import sys
from boto.s3.connection import S3Connection
from boto.s3.key import Key

# get the s3 keys from the settings file
sys.path.append('/Users/jfenton/reporting/reportingsitenew/reportingsite')
from settings import AWS_ACCESS_KEY_ID 
from settings import AWS_SECRET_ACCESS_KEY

# the 
local_backup_dir = "/Users/jfenton/reporting/reportingsitenew/reportingsite/reporting/scripts"

try:
    file_to_upload = sys.argv[1]
except IndexError:
    raise Exception("No upload file specified")
full_file_path = "%s/%s" % (local_backup_dir, file_to_upload)

conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
b = conn.get_bucket('assets.sunlightfoundation.com')
k = Key(b)
s3_string = "reporting/dbbackups/%s" % file_to_upload
k.key = s3_string
k.set_contents_from_filename(full_file_path)

