#!/usr/bin/python
import json, ipdb, httplib, urllib, sys, pickle, time, gpxpy, gpxpy.gpx
from datetime import datetime
from optparse import OptionParser
import glob

print "######################"
print "# GPX File Uploader #"
print "######################"

source = 'gpx tracks'
batch_size = 1000
sleep_between_batches = 10
sleep_on_errors = 30
cache_file_name = 'gpx-tracks.pckl'

parser = OptionParser()
parser.add_option("-d", "--directory", dest="directory", help="directory including gpx files", metavar="FILE")
(options, args) = parser.parse_args()

access_token = raw_input("Access Token: ")

print str(datetime.utcnow()) + " importing files from directory..."
gpx_files = glob.glob(options.directory + "*.gpx")
print str(datetime.utcnow()) + " " + str(len(gpx_files)) + " files retrieved, parsing locations..."

def starting_position():
    try:
        f = open(cache_file_name, 'rb')
        return pickle.load(f)
    except IOError:
        return None

starting_position = starting_position()

if starting_position is None:
    print str(datetime.utcnow()) + " starting from scratch"
else:
    print str(datetime.utcnow()) + " starting from " + str(starting_position)

parsed_locations = []

for gpx_file_name in gpx_files:
    gpx_file = open(gpx_file_name, 'r')
    gpx = gpxpy.parse(gpx_file)

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                params = {
                    'latitude':       str(point.latitude),
                    'longitude':      str(point.longitude),
                    'timestamp':      str(point.time),
                    'source':         source
                }

                if starting_position < params['timestamp']:
                    parsed_locations.append(params)

print str(datetime.utcnow()) + " " + str(len(parsed_locations)) + " locations parsed..."

if len(parsed_locations) == 0:
    print str(datetime.utcnow()) + " no locations to send..."
else:
    print str(datetime.utcnow()) + " sorting locations..."
    sorted_parsed_locations = sorted(parsed_locations, key=lambda k: k['timestamp'])

    print str(datetime.utcnow()) + " grouping locations into batches..."
    location_batches = [sorted_parsed_locations[x:x+batch_size] for x in xrange(0, len(sorted_parsed_locations), batch_size)]

    print str(datetime.utcnow()) + " posting location batches..."
    for i, location_batch in enumerate(location_batches):
        for _ in range(0,100):
            try:
                print str(datetime.utcnow()) + " posting " + str(len(location_batch)) + " locations from " + str(location_batch[0]['timestamp']) + " onwards..."
                # conn = httplib.HTTPConnection(host='localhost', port=3000)
                conn = httplib.HTTPSConnection(host='memair.herokuapp.com', port=443)
                headers = {"Content-type": "application/json"}
                conn.request("POST", "/api/v1/bulk/locations", json.dumps({'json': location_batch, 'access_token': access_token}), headers)
                content = conn.getresponse()
                response = json.loads(content.read())
                conn.close()
                print response
                if "bulk_import_id" in response:
                    f = open(cache_file_name, 'wb')
                    pickle.dump(location_batch[-1]['timestamp'], f)
                    f.close()
                    break
            except:
                print "Unexpected error:", sys.exc_info()[0]

            print "sleeping for " + str(sleep_on_errors) + " seconds and then retrying..."
            time.sleep(sleep_on_errors)

        time.sleep(sleep_between_batches)

print str(datetime.utcnow()) + " done!"
