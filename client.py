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
from furl import furl
from itertools import count, groupby
from dotenv import load_dotenv, find_dotenv
from daemonize import Daemonize
from raven import Client
import math
import os
import random
from __version__ import VERSION as v

load_dotenv(find_dotenv()) # load variables from .env file

# settings
poemRequestTime = 10 # number of seconds between poem requests
lineDisplayTime = 5 # number of seconds between line display updates
displayWidth = 15 # width of display in chars
api_url = os.environ.get('API_URL')
url_root = 'http://127.0.0.1:8000' # location of the Flask API (localhost)
clear_url = url_root + '/clear'
pid = os.environ.get('PIDFILE_LOCATION')
location = os.environ.get('LOCATION')

# create scheduler
s = sched.scheduler(time.time, time.sleep)

# create an error tracker
sentry_client = Client()

# makes the poem request
def getPoem(sc):
    poem = ''
    try:
        u = furl(api_url)
        u.args = {'location': location, 'v': v}
        print "Getting poem from {}.".format(u.url)
        response = urlopen(u.url, timeout=10).read()
        poem = json.loads(response)
        print "Got live poem: {}".format(poem)
    except Exception as e:
        print(e)
        sentry_client.captureException()
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
    callFlippy(clear_url)

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
        line_one_words = words[:top_line_count]
        line_two_words = words[top_line_count-len(words):]

        # sometimes the top line is still over the display width so...
        if (len(' '.join(line_one_words)) > displayWidth):
            line_two_words = [line_one_words.pop()] + line_two_words

        line_one = ' '.join(line_one_words)
        line_two = ' '.join(line_two_words)

    # build our url
    u = furl(url_root)
    u.path.segments = ['naho', line_one]
    if line_two: u.path.segments.append(line_two)

    callFlippy(u.url)

def callFlippy(url):
    try:
        urlopen(url, timeout=10).read()
    except Exception:
        sentry_client.captureException()

# Start the scheduler
def startScheduler():
    s.enter(poemRequestTime, 1, getPoem, (s,))
    s.run()

try:
    daemon = Daemonize(app="ee_client", pid=pid, action=startScheduler)
    daemon.start()
    # startScheduler()
except Exception:
    sentry_client.captureException()
