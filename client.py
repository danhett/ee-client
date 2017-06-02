from urllib2 import Request, urlopen, URLError

request = Request('http://everythingeverytime.herokuapp.com/poem')

try:
	response = urlopen(request)
	poem = response.read()
	print poem
except URLError, e:
    print 'Whoops. Got an error code:', e
