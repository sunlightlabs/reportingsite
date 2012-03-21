""" Util to download the zipped, raw fec files from the FEC ftp site and unzip them directly to the filecache directory. If we do this ahead of time, we don't need to hit their site tons of times to backfill / analyze older data. Assumes we can use unzip at the cmd prompt... """

from datetime import date, timedelta
from urllib2 import Request, urlopen
from os import system
from time import sleep

from outside_spending_settings import fec_file_location, user_agent, zip_directory, filecache_directory

# Note that 2011/12/04 is missing

# todo: take these as cmd line args
start_date = date(2012,3,14)
end_date = date(2012,3,19)

one_day = timedelta(days=1)


def download_with_headers(url):
    """ Sign our requests with a user agent"""
    headers = { 'User-Agent' : user_agent }    
    req = Request(url, None, headers)
    return urlopen(req).read()

this_date = start_date
while (this_date < end_date):
    datestring = this_date.strftime("%Y%m%d")
    file_to_download = fec_file_location % datestring
    print "Downloading: %s" % (file_to_download)
    this_date += one_day
    downloaded_zip_file = zip_directory + "/" + datestring + ".zip"
    dfile = open(downloaded_zip_file, "w")
    dfile.write(download_with_headers(file_to_download))
    dfile.close()
    
    # Now unzip 'em 
    cmd = "unzip -o %s -d %s" % (downloaded_zip_file, filecache_directory)
    print "Now unzipping with %s" % (cmd)
    system(cmd)
    
    # Pause for a second
    print "Now sleeping for a second."
    sleep(1)
