from django.conf import settings

#BASE_DIR = '/projects/reporting/src/reportingsite/outside_spending'
#BASE_DIR = '/Users/jfenton/reporting/reportingsitenew/reportingsite/outside_spending'
BASE_DIR = settings.FEC_BASE_DIR

# where can we save local files?
#FILECACHE_DIRECTORY = BASE_DIR + '/data/fec_filings'
FILECACHE_DIRECTORY = settings.FEC_FILECACHE_DIRECTORY

# where can we save raw zip files downloaded from the FEC before unzipping
ZIP_DIRECTORY = BASE_DIR + '/data/zipped_fec_filings'

# where are NYT's csv definitional files? These are generally swiped from here, and fixed up (some of them need tweaking): https://github.com/NYTimes/Fech/tree/master/sources -- or maybe bycoffe's branch: https://github.com/NYTimes/Fech/tree/huffingtonpost/sources
CSV_FILE_DIRECTORY = BASE_DIR + '/sources'

# where does the FEC keep the zip files in bulk ? 
FEC_FILE_LOCATION = "ftp://ftp.fec.gov/FEC/electronic/%s.zip"

# where are the raw .fec files located? 
FEC_DOWNLOAD = "http://query.nictusa.com/dcdev/posted/%s.fec"

# How should our requests be signed? 
USER_AGENT = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"

# what cycle is it now? 
CYCLE = 2012

# scraper delay time, in seconds
DELAY_TIME=2

LOG_DIRECTORY = BASE_DIR + "/log/"
LOG_NAME = "outside_spending"

MAX_FILING_KEY = "max-filing-number"
LAST_PROCESS_KEY="last-process-time"

