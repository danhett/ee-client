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
from itertools import count, groupby
import math

# settings
isLocal = False  # sets localhost/remote
poemRequestTime = 10 # number of seconds between poem requests
lineDisplayTime = 5 # number of seconds between line display updates
remote_url = 'http://everythingeverytime.herokuapp.com/poem'
test_url = 'http://localhost:8080/poem'
url_root = 'http://192.168.1.125' # location of the Flask API
sign_url_two_line = url_root + '/naho/0/0/'
sign_url_one_line = url_root + '/nahosingle/'
clear_url = url_root + '/clear'

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

    print "Got live poem:"
    print poem

    printLines(poem['poem'])

    s.enter(poemRequestTime, 1, getPoem, (sc,))

# Processes each poem line on a delay
def printLines(poem):
    for i in poem:
        time.sleep(lineDisplayTime)
        #sendLineToSign(quote(i, safe=''))
        sendLineToSign(i)

    # now the poem is finshed, erase the display until the next cycle
    time.sleep(lineDisplayTime)
    clearReq = urllib2.urlopen(clear_url)
    clearReq.read()

# Sends a single line to the sign
def sendLineToSign(line):
    line1 = ""
    line2 = ""

    print "Sending line:" + line

    counts = len(line.lower().split())

    # if long sentence, split over two lines
    if(counts > 4):
        halfCounts = math.ceil((counts+1)/2)

        halves = split_lines(line, halfCounts)

        line1 = quote(halves[0])

        if len(halves) > 1:
            line2 = quote(halves[1], safe='')
        else:
            line2 = quote(" ", safe='')

        sendURL = sign_url_two_line + line1 + "/" + line2
    
    # else put on a single line
    else:
	sendURL = sign_url_one_line + quote(line, safe='')

    signReq = urllib2.urlopen(sendURL)
    signReq.read()

def split_lines(sentence, step=4):
    c = count()
    chunks = sentence.split()
    return [' '.join(g) for k, g in groupby(chunks, lambda i: c.next() // step)]

# Start the scheduler
s.enter(poemRequestTime, 1, getPoem, (s,))
s.run()
