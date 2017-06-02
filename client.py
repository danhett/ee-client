import urllib2
import json

url = 'http://everythingeverytime.herokuapp.com/poem'

httpreq = urllib2.urlopen(url)
response = httpreq.read()
poem = json.loads(response)

for i in poem['poem']:
    print i
