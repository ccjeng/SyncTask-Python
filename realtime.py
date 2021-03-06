#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import sys
import logging
import geocoder
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

    for item in items:
        addr = item['location']
        g = geocoder.google(addr)

        if g.ok:
            data = {'lineid': item['lineid'], 'car': item['car'], 'address': addr,
                    'time': item['time'], 'lat': g.lat, 'lng': g.lng}
            result = firebase.post(stgTable, data)
        else:
            print(g.json)
        time.sleep(0.5)

    # Copy to PROD
    print('Copy to PROD')
    firebase.delete('/PROD', None)
    stgResults = firebase.get(stgTable, None)
    firebase.patch('/PROD', stgResults)
    print('Done')


sched = BlockingScheduler()
logging.basicConfig()

main()


def err_listener(event):
    print('%s' % (event))


sched.add_listener(
    err_listener, events.EVENT_SCHEDULER_START | events.EVENT_JOB_ERROR | events.EVENT_JOB_MISSED)


@sched.scheduled_job('interval', minutes=5)
def timed_job():
    try:
        main()
    except Exception as e:
        print(e)

sched.start()
