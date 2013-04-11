"""  Stuff to make a 1-level python hash into a postgres-style hstore that can be mushed into a mysql text field.  Everything is stored as text and must be converted back to a number, if appropriate.

This is in contrast to 

"""



from cStringIO import StringIO
import re

class HStoreDecodeError(Exception):
    pass

def dict_to_hstore(python_dict):
    """ 
    There's an implementation of this here ( HstoreAdapter ) https://github.com/psycopg/psycopg2/blob/master/lib/extras.py
    but the comments say that it is "painfully inefficient!"
    
    """
    hstore = StringIO()
    first_row = True
    for key in python_dict:
        ## Prune the hash--if it's empty
        value = python_dict[key]
        if value:
            if not first_row:
                hstore.write("|")
            else:
                first_row=False
            # don't allow quotes within the value. Not sure if we should check this here. 
            value = value.replace('"','')
            hstore.write("\"%s\"=>\"%s\"" % (key, value)
    return hstore.getvalue()
    

## If we were using a comma as a delimiter, we'd need to use a regex to allow for the possibility that a comma was inside the commas--so use the below. But we don't have to do that if we use the bar as delimiter. We already clean bars out in utf8clean.

# key_pair_re = re.compile('"(.+?)"=>"(.+?)"(?:,|$)')
key_pair_re = re.compile('"(.+?)"=>"(.+?)"')
def hstore_to_dict(text_string):
    return_dict = {}
    keypairs = text_string.split("|")
    for keypair in keypairs:
        keygroups = re.find(key_pair_re, keypair)
        return_dict[keygroups[1]]=keygroups[2]
    return return_dict
    
    
    
    