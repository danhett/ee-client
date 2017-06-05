import urllib2
import json
import time
import sched
from urllib import quote

# Set this to use localhost
isLocal = True

poemRequestTime = 5

remoteurl = 'http://everythingeverytime.herokuapp.com/poem'
testurl = 'http://localhost:8080/poem'

if isLocal:
    url = testurl
else:
    url = remoteurl

# Creates a scheduler to make our API calls
s = sched.scheduler(time.time, time.sleep)

def getPoem(sc):
    print "Getting poem..."

    httpreq = urllib2.urlopen(url)
    response = httpreq.read()
    poem = json.loads(response)

    line = quote(poem["poem"][0], safe='')
    print "Sending line: " + line

    s.enter(poemRequestTime, 1, getPoem, (sc,))

# Start the scheduler
s.enter(poemRequestTime, 1, getPoem, (s,))
s.run()


#sendURL = 'http://192.168.125.47/small/2/2/' + line
#signReq = urllib2.urlopen(sendURL)
#signReq.read()
