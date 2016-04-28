#!/usr/bin/python
import json, ipdb, httplib, urllib, sys
from datetime import datetime
from optparse import OptionParser

print "####################################"
print "# Google Takeout Location Uploader #"
print "####################################"

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename", help="extracted LocationHistory.json file", metavar="FILE")
(options, args) = parser.parse_args()

access_token = raw_input("Access Token: ")

print "Importing file..."
with open(options.filename) as json_file:
  json_data = json.load(json_file)

locations = json_data['locations']
locations_count = len(locations)
source = 'google location services'

print str(locations_count) + " locations retrieved... uploading"

for i, location in enumerate(locations):
  timestamp = datetime.fromtimestamp(int(location['timestampMs'])/1000.0)
  latitude = location['latitudeE7'] * 0.0000001
  longitude = location['longitudeE7'] * 0.0000001
  accuracy = location['accuracy']

  params = {
    'latitude':       str(latitude),
    'longitude':      str(longitude),
    'timestamp':      str(timestamp),
    'point_accuracy': str(accuracy),
    'source':         source,
    'access_token':   access_token
  }

  if 'activitys' in location.keys():
    params['notes'] = json.dumps(location['activitys'], ensure_ascii=False)

  conn = httplib.HTTPSConnection(host="memair.herokuapp.com", port=443)
  encoded_params = urllib.urlencode(params)

  conn.request("POST", "/api/v1/locations", encoded_params)
  content = conn.getresponse()
  conn.close()

  percent = ((i+1) / float(locations_count)) * 100
  sys.stdout.write("# Progress: %d%%       \r" % (percent) )
  sys.stdout.flush()

print
print "Done!"
