import base64
try:
    import json
except ImportError:
    import simplejson as json
import socket
import time
import urllib2

import MultipartPostHandler


socket.setdefaulttimeout(25)

USERNAME = ''
PASSWORD = ''

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

    params = {'title': str(committee.name).title(),
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


def doccloud_update(sender, **kwargs):
    import urllib
    committee = kwargs['instance']

    params = {'title': str(committee.name).title(),
              '_method': 'put', }
    url = 'https://www.documentcloud.org/api/documents/%s.json' % committee.doc_id
    opener = urllib2.build_opener()
    request = urllib2.Request(url, urllib.urlencode(params))
    auth = base64.encodestring('%s:%s' % (USERNAME, PASSWORD))[:-1]
    request.add_header('Authorization', 'Basic %s' % auth)

    ret = opener.open(request).read()
    print ret
