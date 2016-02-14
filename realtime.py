#!/usr/bin/python
# -*- coding: utf-8 -*-

import geocoder
import requests
from firebase import firebase

firebase = firebase.FirebaseApplication(
    'https://tptrashcarrealtime.firebaseio.com/', None)

url = 'http://data.ntpc.gov.tw/od/data/api/28AB4122-60E1-4065-98E5-ABCCB69AACA6?$format=json'

response = requests.get(url)
items = response.json()

# STG
firebase.delete('/STG', None)

print('count = ' + str(len(items)))

for item in items:
    g = geocoder.google(item['location'])
    data = {'lineid': item['lineid'], 'car': item['car'], 'address': item['location'],
            'time': item['time'], 'lat': g.lat, 'lng': g.lng}
    result = firebase.post('/STG', data)
    print(item['lineid'] + ',' + str(g.lat) + ',' + str(g.lng))


# Copy to PROD
firebase.delete('/PROD', None)
stgResults = firebase.get('/STG', None)
firebase.patch('/PROD', stgResults)
