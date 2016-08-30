# Python-Importer for [Memair](http://Memair.com)
Example Python scripts for importing data into Memair.

## Google Takeout Location Importer
Download location histroy in json fromat from [Google Takeout](https://takeout.google.com/settings/takeout). Extract the LocationHistory.json file.

Run: `$ python google-takeout-location.py -f PATH/TO/LocationHistory.json`

The script will prompt you for an access token which you can create [here](https://memair.herokuapp.com/generate_own_access_token).

## GPX Importer
Place all of the gpx files in a single directory.

Run: `$ python gpx-importer.py -d PATH/TO/DIRECTORY/CONTAINING/GPX/FILES/`

The script will prompt you for an access token which you can create [here](https://memair.herokuapp.com/generate_own_access_token).

## CSV Importer
Locations in csv files are not stored in a standard way so this importer will need to be updated to suit your specific csv files. Once the importer is updated, place all of the csv files in a single directory.

Run: `$ python csv-importer.py -d PATH/TO/DIRECTORY/CONTAINING/CSV/FILES/`

The script will prompt you for an access token which you can create [here](https://memair.herokuapp.com/generate_own_access_token).
