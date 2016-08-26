#!/usr/bin/python
import json, ipdb, httplib, urllib, sys, pickle, time
from datetime import datetime
from optparse import OptionParser

print "####################################"
print "# Google Takeout Location Uploader #"
print "####################################"

source = 'google location services'
batch_size = 1000
sleep_between_batches = 300
sleep_on_errors = 30

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename", help="extracted LocationHistory.json file", metavar="FILE")
(options, args) = parser.parse_args()

access_token = raw_input("Access Token: ")

print str(datetime.utcnow()) + " importing file..."
with open(options.filename) as json_file:
  json_data = json.load(json_file)
locations = json_data['locations']
locations_count = len(locations)
print str(datetime.utcnow()) + " " + str(locations_count) + " locations retrieved, parsing locations..."

def starting_position():
  try:
    f = open('store.pckl', 'rb')
    return pickle.load(f)
  except IOError:
    return None

starting_position = starting_position()

if starting_position is None:
  print str(datetime.utcnow()) + " starting from scratch"
else:
  print str(datetime.utcnow()) + " starting from " + str(starting_position)

parsed_locations = []

for i, location in enumerate(locations):
  timestamp = datetime.fromtimestamp(int(location['timestampMs'])/1000.0)
  latitude = location['latitudeE7'] * 0.0000001
  longitude = location['longitudeE7'] * 0.0000001

  params = {
    'latitude':       str(latitude),
    'longitude':      str(longitude),
    'timestamp':      str(timestamp),
    'source':         source
  }

  if 'activitys' in location.keys():
    params['notes'] = json.dumps(location['activitys'], ensure_ascii=False)

  if 'accuracy' in location.keys():
    params['point_accuracy'] = str(location['accuracy'])

  if starting_position < params['timestamp']:
    parsed_locations.append(params)

print str(datetime.utcnow()) + " " + str(len(parsed_locations)) + " locations parsed..."

print str(datetime.utcnow()) + " sorting locations..."
sorted_parsed_locations = sorted(parsed_locations, key=lambda k: k['timestamp'])

print str(datetime.utcnow()) + " grouping locations into batches..."
location_batches = [sorted_parsed_locations[x:x+batch_size] for x in xrange(0, len(sorted_parsed_locations), batch_size)]

print str(datetime.utcnow()) + " posting location batches..."
for i, location_batch in enumerate(location_batches):
  for _ in range(0,100):
    try:
      print str(datetime.utcnow()) + " posting " + str(len(location_batch)) + " locations from " + str(location_batch[0]['timestamp']) + " onwards..."
    #   conn = httplib.HTTPConnection(host='localhost', port=3000)
      conn = httplib.HTTPSConnection(host='memair.herokuapp.com', port=443)
      headers = {"Content-type": "application/json"}
      conn.request("POST", "/api/v1/bulk/locations", json.dumps({'json': location_batch, 'access_token': access_token}), headers)
      content = conn.getresponse()
      response = json.loads(content.read())
      conn.close()
      print response
      if "bulk_import_id" in response:
        f = open('store.pckl', 'wb')
        pickle.dump(location_batch[-1]['timestamp'], f)
        f.close()
        break
    except:
      print "Unexpected error:", sys.exc_info()[0]

    print "sleeping for " + str(sleep_on_errors) + " seconds and then retrying..."
    time.sleep(sleep_on_errors)

  time.sleep(sleep_between_batches)

print str(datetime.utcnow()) + " done!"

f.close()
