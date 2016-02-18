#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import logging
from googlegeocoder import GoogleGeocoder
import requests
from firebase import firebase
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler import events

firebase = firebase.FirebaseApplication(
    'https://tptrashcarrealtime.firebaseio.com/', None)
stgTable = 'STG_Heroku'


def main():
    url = 'http://data.ntpc.gov.tw/od/data/api/28AB4122-60E1-4065-98E5-ABCCB69AACA6?$format=json'

    response = requests.get(url)
    response.encoding = 'UTF-8'
    items = response.json()

    # STG
    firebase.delete(stgTable, None)

    print('count = ' + str(len(items)))

    geocoder = GoogleGeocoder()

    for item in items:
        addr = item['location']
        search = geocoder.get(addr)

        lat = search[0].geometry.location.lat
        lng = search[0].geometry.location.lng

        if lat > 0:
            data = {'lineid': item['lineid'], 'car': item['car'], 'address': addr,
                    'time': item['time'], 'lat': lat, 'lng': lng}
            result = firebase.post(stgTable, data)
        else:
            print(search)

    # Copy to PROD
    print('Copy to PROD')
    firebase.delete('/PROD', None)
    stgResults = firebase.get(stgTable, None)
    firebase.patch('/PROD', stgResults)
    print('Done')


sched = BlockingScheduler()
logging.basicConfig()

#main()


def err_listener(event):
    print('%s' % (event))


sched.add_listener(
    err_listener, events.EVENT_SCHEDULER_START | events.EVENT_JOB_ERROR | events.EVENT_JOB_MISSED)


@sched.scheduled_job('interval', minutes=4)
def timed_job():
    main()

sched.start()
