
base_dir = '/Users/jfenton/reporting/reportingsitenew/reportingsite/outside_spending'


# where can we save local files?
filecache_directory = base_dir + '/data/fec_filings'

# where can we save raw zip files downloaded from the FEC before unzipping
zip_directory = base_dir + '/data/zipped_fec_filings'


# where are NYT's csv definitional files? These are generally swiped from here, and fixed up (some of them need tweaking): https://github.com/NYTimes/Fech/tree/master/sources -- or maybe bycoffe's branch: https://github.com/NYTimes/Fech/tree/huffingtonpost/sources
csv_file_directory = base_dir + '/sources'


# where does the FEC keep the files ? 
fec_file_location = "ftp://ftp.fec.gov/FEC/electronic/%s.zip"

fed_download = "http://query.nictusa.com/dcdev/posted/%s.fec"

# How should our requests be signed? 
user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"

# what cycle is it now? 
cycle = 2012


