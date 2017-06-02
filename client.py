import urllib2
import json
from urllib import quote

print "Getting poem..."

url = 'http://everythingeverytime.herokuapp.com/poem'

httpreq = urllib2.urlopen(url)
response = httpreq.read()
poem = json.loads(response)

#for i in poem['poem']:
#    print i


line = quote(poem["poem"][0], safe='')
print "Sending line: " + line

sendURL = 'http://192.168.125.47/small/2/2/' + line

signReq = urllib2.urlopen(sendURL)
signReq.read()
