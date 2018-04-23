import requests
import json

def get_distance_duration(origin, destination):
	url = "https://maps.googleapis.com/maps/api/distancematrix/json"
	querystring = {"origins":origin,"destinations":destination,"mode":"driving","units":"imperial","key":"AIzaSyBFtZqrpYnu-tGr_YmStux8K1RPOpU0XmY"}
	response = requests.request("POST", url, params=querystring)

	r = json.loads(response.text)
	distance = r['rows'][0]['elements'][0]['distance']
	duration = r['rows'][0]['elements'][0]['duration']

	return distance, duration