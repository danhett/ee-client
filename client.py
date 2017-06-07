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
isLocal = False  # sets localhost/remote
poemRequestTime = 60 # number of seconds between poem requests
lineDisplayTime = 5 # number of seconds between line display updates
remote_url = 'http://everythingeverytime.herokuapp.com/poem'
test_url = 'http://localhost:8080/poem'
sign_url = 'http://192.168.1.115/small/2/2/'

# setup
if isLocal:
    url = test_url
else:
    url = remote_url


# create scheduler
s = sched.scheduler(time.time, time.sleep)

# makes the poem request
def getPoem(sc):
    print "Getting poem..."

    httpreq = urllib2.urlopen(url)
    response = httpreq.read()
    poem = json.loads(response)

    printLines(poem['poem'])

    s.enter(poemRequestTime, 1, getPoem, (sc,))

# Processes each poem line on a delay
def printLines(poem):
    for i in poem:
        time.sleep(lineDisplayTime)
        sendLineToSign(quote(i, safe=''))

# Sends a single line to the sign
def sendLineToSign(line):
    print line
    sendURL = sign_url + line
    signReq = urllib2.urlopen(sendURL)
    signReq.read()

# Start the scheduler
s.enter(poemRequestTime, 1, getPoem, (s,))
s.run()
