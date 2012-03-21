if __name__ == '__main__':
    # run through all the files we've got and test something
    
    version_hash={}
    
    for directory, dirnames, filenames in os.walk('/Users/jfenton/reporting/reportingsite/rebuckley/data/fec_filings'):
        for i in filenames:
        
    
        
        
        f1 = filing(f)
        f1.download()
        print f1.get_headers()
        print f1.get_rows('SA')