from google.appengine.api import urlfetch
import urllib
import json

def get_distance_duration(origin, destination):
	querystring = {"origins":origin,"destinations":destination,"units":"imperial", "key":"AIzaSyAKs05GprFA_ZxAoHcmIXS3ZZXVMPxtwb8"}
	url = "https://maps.googleapis.com/maps/api/distancematrix/json?%s" % urllib.urlencode(querystring)
	response = urlfetch.fetch(url=url, method=urlfetch.POST)

	r = json.loads(response.content)
	distance = r['rows'][0]['elements'][0]['distance']
	duration = r['rows'][0]['elements'][0]['duration']

	return distance, duration