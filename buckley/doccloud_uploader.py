import base64
try:
    import json
except ImportError:
    import simplejson as json
import socket
import time
import urllib2

import MultipartPostHandler

"""
{u'description': None, u'title': u'CONSERVATIVES FOR TRUTH', u'id': u'8454-conservatives-for-truth', u'canonical_url': u'http://www.documentcloud.org/documents/8454-conservatives-for-truth.html', u'annotations': [], u'sections': [], u'pages': 0, u'resources': {u'pdf': u'https://www.documentcloud.org/documents/8454/conservatives-for-truth.pdf', u'search': u'https://www.documentcloud.org/documents/8454/search.json?q={query}', u'page': {u'text': u'https://www.documentcloud.org/documents/8454/pages/conservatives-for-truth-p{page}.txt', u'image': u'https://www.documentcloud.org/documents/8454/pages/conservatives-for-truth-p{page}-{size}.gif'}, u'thumbnail': u'https://s3.amazonaws.com:443/s3.documentcloud.org/documents%2F8454%2Fpages%2Fconservatives-for-truth-p1-thumbnail.gif?Signature=XG%2BPwY4DvTdhB%2BDLCf5mPwSjvzY%3D&Expires=1284582520&AWSAccessKeyId=AKIAILH45M5OFUTSFEZQ', u'text': u'https://www.documentcloud.org/documents/8454/conservatives-for-truth.txt'}
"""

socket.setdefaulttimeout(25)

USERNAME = '***REMOVED***'
PASSWORD = '***REMOVED***'

def doccloud_upload(sender, **kwargs):
    """Via http://www.muckrock.com/blog/using-the-documentcloud-api/
    """
    committee = kwargs['instance']
    if committee.doc_id:
        return

    filename = r'/tmp/fec.pdf'
    tf = open(filename, 'wb')
    tf.write(urllib2.urlopen(committee.pdf_url).read())
    tf.close()

    params = {'title': str(committee.name),
              'source': 'FEC',
              'file': open(filename, 'rb'),
              'access': 'public',
              }
    url = '/upload.json'
    opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)
    request = urllib2.Request('https://www.documentcloud.org/api/%s' % url, params)
    auth = base64.encodestring('%s:%s' % (USERNAME, PASSWORD))[:-1]
    request.add_header('Authorization', 'Basic %s' % auth)

    try:
        ret = opener.open(request).read()
        info = json.loads(ret)
        committee.doc_id = info['id']
        committee.save()
    except urllib2.URLError, exc:
        pass

    time.sleep(1)
