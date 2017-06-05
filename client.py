"""
<every thing, every time>
client.py

@author Dan Hett (hellodanhett@gmail.com)

This is a small python script designed to manage the signs for Naho Matsuda's
'every thing, every time' artwork for CityVerve. Specifically, it handles
timed queries to the API to grab poems, and then outputs the lines to the
displays, timed appropriately to work correctly with the hardware.
"""
import urllib2
import json
import time
import sched
from urllib import quote

# settings
isLocal = True  # sets localhost/remote
poemRequestTime = 5 # number of seconds between poem requests
remoteurl = 'http://everythingeverytime.herokuapp.com/poem'
testurl = 'http://localhost:8080/poem'

# setup
if isLocal:
    url = testurl
else:
    url = remoteurl


# create scheduler
s = sched.scheduler(time.time, time.sleep)

# makes the poem request
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

# TODO - this will output to the signs
#sendURL = 'http://192.168.125.47/small/2/2/' + line
#signReq = urllib2.urlopen(sendURL)
#signReq.read()
