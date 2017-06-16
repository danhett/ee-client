"""
<every thing, every time>
client.py

@author Dan Hett (hellodanhett@gmail.com)

This is a small python script designed to manage the signs for Naho Matsuda's
'every thing, every time' artwork for CityVerve. Specifically, it handles
timed queries to the API to grab poems, and then outputs the lines to the
displays, timed appropriately to work correctly with the hardware.
"""
import json
import time
import sched
from urllib import quote
from urllib2 import urlopen
from urlparse import urljoin
from itertools import count, groupby
from dotenv import load_dotenv, find_dotenv
from daemonize import Daemonize
import math
import os
import random

load_dotenv(find_dotenv()) # load variables from .env file

# settings
poemRequestTime = 10 # number of seconds between poem requests
lineDisplayTime = 5 # number of seconds between line display updates
displayWidth = 15 # width of display in chars
url = os.environ.get('API_URL')
url_root = 'http://127.0.0.1:8000' # location of the Flask API (localhost)
clear_url = url_root + '/clear'
naho_url = url_root + '/naho/'
pid = os.environ.get('PIDFILE_LOCATION')

# create scheduler
s = sched.scheduler(time.time, time.sleep)

# makes the poem request
def getPoem(sc):
    print "Getting poem..."

    poem = ''
    try:
        response = urlopen(url).read()
        poem = json.loads(response)
        print "Got live poem: {}".format(poem)
    except Exception as e:
        print "Arg fale: {}".format(e)
        poems = ''
        with open('poems.json') as data:
            poems = json.load(data)
        poem = random.choice(poems)
        print "Got backup poem: {}".format(poem)

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
    urlopen(clear_url).read()

# Sends a single line to the sign
def sendLineToSign(line):
    print "Sending line: {}".format(line)

    line_one = ''
    line_two = ''
    char_count = len(line.lower())

    if char_count <= displayWidth:
        line_one = line
    else:
        # count the words in the first half of the line then split on this
        top_line_count = len(line[:char_count/2].strip().split())
        words = line.strip().split()
        line_one = ' '.join(words[:top_line_count])
        line_two = ' '.join(words[top_line_count-len(words):])

    url = urljoin(naho_url, quote(line_one, safe=''))
    if line_two:
        url = urljoin(url+'/', quote(line_two, safe=''))

    try:
        print(url)
        urlopen(url).read()
    except Exception as e:
        print e

# Start the scheduler
def startScheduler():
    s.enter(poemRequestTime, 1, getPoem, (s,))
    s.run()

daemon = Daemonize(app="ee_client", pid=pid, action=startScheduler)
daemon.start()
