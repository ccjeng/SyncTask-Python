#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import logging
import geocoder
import requests
from firebase import firebase
from apscheduler.schedulers.blocking import BlockingScheduler

firebase = firebase.FirebaseApplication(
    'https://tptrashcarrealtime.firebaseio.com/', None)
stgTable = 'STG_Heroku'


def main():

    url = 'http://data.ntpc.gov.tw/od/data/api/28AB4122-60E1-4065-98E5-ABCCB69AACA6?$format=json'

    response = requests.get(url)
    items = response.json()

    # STG
    firebase.delete(stgTable, None)

    print('count = ' + str(len(items)))

    for item in items:
        g = geocoder.google(item['location'])
        if g.lat > 0:
            data = {'lineid': item['lineid'], 'car': item['car'], 'address': item['location'],
                    'time': item['time'], 'lat': g.lat, 'lng': g.lng}
            result = firebase.post(stgTable, data)
        else:
            print(item['lineid'] + ',' + str(g.lat) + ',' + str(g.lng))

    # Copy to PROD
    print('Copy to PROD')
    firebase.delete('/PROD', None)
    stgResults = firebase.get(stgTable, None)
    firebase.patch('/PROD', stgResults)
    print('Done')

main()

sched = BlockingScheduler()
logging.basicConfig()


@sched.scheduled_job('interval', minutes=5)
def timed_job():
    main()

sched.start()
