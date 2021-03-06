"""
Call the Daily Historical endpoint and put the data into a CSV file
"""

import argparse

import requests


APP_ID = 'YOUR_APP_ID_HERE'
APP_KEY = 'YOUR_APP_KEY_HERE'

ENDPOINT = 'historical/daily'

data = []

##############################
# Setting up argument parser #
parser = argparse.ArgumentParser(description='Makes a call to the Daily Historical endpoint and converts the JSON return object to a CSV file.')

required = parser.add_argument_group('additional required arguments')
required.add_argument('-l', '--location',
                      required=True,
                      help='Latitude and longitude coordinates in decimal degrees.',
                      metavar= '<lat>,<lon>')
required.add_argument('-s', '--start',
                      required=True,
                      help='Start time of the data returned',
                      metavar='timestamp')
required.add_argument('-e', '--end',
                      required=True,
                      help='End time of the data returned',
                      metavar='timestamp')
parser.add_argument('-u', '--unitcode',
                    required=False,
                    choices=['us-std',
                             'si-std',
                             'us-std-precise',
                             'si-std-precise'],
                    help='Unit conversion set to be used. ')
args = parser.parse_args()

def _unpack_data(d, previous_key):
    for k, v in d.items():
        if isinstance(v, dict):
            _unpack_data(v, k)
        elif previous_key is None and isinstance(v, int):
            data.append((k, v))
        else:
            data.append((previous_key + '_' + k, v))
        # else
# def unpackData



first = True
parameters = ({'app_id': APP_ID,
               'app_key': APP_KEY,
               'location': args.location,
               'start': args.start,
               'end': args.end,
               'unitcode': args.unitcode})

response = requests.get('http://ag.clearapis.com/v1.2/' + ENDPOINT,
                        params=parameters)

### Check if response is valid.
if response.status_code != 200:
    print '========= ERROR ========='
    print 'Status code: ' + str(response.status_code)
    print 'Parameters: ' + str(parameters)
    print 'URL: ' + response.url
    print '========================='
    exit(0)
# if

print 'Succesfully called endpoint at:'
print response.url

j_response = response.json()

file_name = ENDPOINT.replace('/', '_') + '.csv'

print 'Creating output file.'
output = open(file_name, 'w')

print 'Reading response to get column titles...'
#### Get column titles
if first:
    data = []
    _unpack_data(j_response.values()[0].values()[0], None)
    output.write('latitude,longitude,time,')
    for k, v in data:
        output.write(str(k)  + ',')
    output.write('\n')
    first = False
# if

print 'Reading each row of data...'
### Get each row of data
# In this current implementation, this programme does not accept multiple
# locations, however the daily historical endpoint can accept up to 5 locations,
# therefore this loop would be needed to allow multiple pairs of coordinates.
for coordinates, times in j_response.items():
    for time, d in times.items():
        data = []
        _unpack_data(d, None)
        print data
        output.write(coordinates + ',' + time + ',')
        for key, value in data:
            output.write(str(value) + ',')
        output.write('\n')
    # for time, d in times.items():
# for coordinates, day in j_response.items():

print 'Done!'
print 'Output file name: ' + file_name
output.close()
