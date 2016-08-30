# Python-Importer for [Memair](http://Memair.com)
Example Python scripts for importing data into Memair.

## Google Locations
Download location histroy in json fromat from [Google Takeout](https://takeout.google.com/settings/takeout). Extract the LocationHistory.json file.

Run: `$ python google-takeout-location.py -f PATH/TO/LocationHistory.json`

The script will prompt you for an access token which you can create [here](https://memair.herokuapp.com/generate_own_access_token).

## GPX Importer
Place all gpx files in a single directory.

Run: `$ python gpx-importer.py -d PATH/TO/DIRECTORY/CONTAINING/GPX/FILES/`

The script will prompt you for an access token which you can create [here](https://memair.herokuapp.com/generate_own_access_token).
