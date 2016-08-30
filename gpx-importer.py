#!/usr/bin/python
import json
import ipdb
import httplib
import urllib
import sys
import pickle
import time
import gpxpy
import gpxpy.gpx
import glob
import logging
from datetime import datetime
from optparse import OptionParser

source = 'gpx file'
batch_size = 1000
sleep_between_batches = 30
sleep_on_errors = 30
cache_file_name = 'gpx-tracks.pckl'

def starting_position():
    try:
        f = open(cache_file_name, 'rb')
        return pickle.load(f)
    except IOError:
        return None

# Set logging
logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(message)s', level=logging.INFO)
logging.info("#####################")
logging.info("# GPX File Uploader #")
logging.info("#####################")

# Get input params
parser = OptionParser()
parser.add_option("-d", "--directory", dest="directory", help="directory including gpx files", metavar="FILE")
(options, args) = parser.parse_args()
access_token = raw_input("Access Token: ")

logging.info("importing files from '" + options.directory + "'")
gpx_files = glob.glob(options.directory + "*.gpx")

if len(gpx_files) == 0:
    logging.error("no gpx found in '" + options.filename + "'")
    logging.error("exiting!")
    sys.exit()

logging.info(str(len(gpx_files)) + " files retrieved, parsing locations...")

# Calculating starting position
starting_position = starting_position()
if starting_position is None:
    logging.info("starting from scratch")
else:
    logging.info("starting from " + str(starting_position))


parsed_locations = []
for gpx_file_name in gpx_files:
    gpx_file = open(gpx_file_name, 'r')
    gpx = gpxpy.parse(gpx_file)

    for waypoint in gpx.waypoints:
        params = {
            'latitude':       str(waypoint.latitude),
            'longitude':      str(waypoint.longitude),
            'timestamp':      str(waypoint.time),
            'source':         source + " - waypoints from " + gpx_file_name
        }

        if starting_position < params['timestamp']:
            parsed_locations.append(params)

    for route in gpx.routes:
        params = {
            'latitude':       str(route.latitude),
            'longitude':      str(route.longitude),
            'timestamp':      str(route.time),
            'source':         source + " - routes from " + gpx_file_name
        }

        if starting_position < params['timestamp']:
            parsed_locations.append(params)

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                params = {
                    'latitude':       str(point.latitude),
                    'longitude':      str(point.longitude),
                    'timestamp':      str(point.time),
                    'source':         source + " - tracks from " + gpx_file_name
                }

                if starting_position < params['timestamp']:
                    parsed_locations.append(params)

if len(parsed_locations) == 0:
    logging.info("no locations to send...")
    sys.exit()

logging.info(str(len(parsed_locations)) + " locations parsed...")
logging.info("sorting locations...")
sorted_parsed_locations = sorted(parsed_locations, key=lambda k: k['timestamp'])

logging.info("grouping locations into batches...")
location_batches = [sorted_parsed_locations[x:x+batch_size] for x in xrange(0, len(sorted_parsed_locations), batch_size)]

locations_sent = 0
locations_to_send = len(sorted_parsed_locations)

logging.info("posting location batches...")
for i, location_batch in enumerate(location_batches):
    for _ in range(0,100):
        try:
            logging.info("posting " + str(len(location_batch)) + " locations from " + str(location_batch[0]['timestamp']) + " onwards...")
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
                locations_sent += len(location_batch)
                logging.info(str(locations_sent) + " of " + str(locations_to_send) + " locations sent...")
                break
            if "Token was unauthorized" in response:
                logging.error("supplied token was not valid")
                logging.error("generate a valid token at https://memair.herokuapp.com/generate_own_access_token!")
                sys.exit()
        except:
            print "Unexpected error:", sys.exc_info()[0]

        print "sleeping for " + str(sleep_on_errors) + " seconds and then retrying..."
        time.sleep(sleep_on_errors)

    time.sleep(sleep_between_batches)

logging.info("done!")
