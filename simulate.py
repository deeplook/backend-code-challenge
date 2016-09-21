#!/usr/bin/env python

"""
Tool for creating a pool of moving vehicles emitting GPS data.
"""

import sys
import uuid
import time
import random
import asyncio
import sqlite3
import configparser
import argparse

import requests

from utils import distance, destination


config_path = 'config.ini'
config = configparser.ConfigParser()
config.read(config_path)
port = config.get('SERVICE', 'port')
endpoint = config.get('SERVICE', 'endpoint')
url = 'http://localhost:%s%s' % (port, endpoint)
path = config.get('SERVICE', 'database')
conn = sqlite3.connect(path)

km_h_to_m_s = 1000 / 3600


class Vehicle(object):
    '''
    A vehicle, able to move and store its state into a database or via an API endpoint.
    '''

    allowed_types = ['bus', 'taxi', 'tram', 'train']
    update_interval = 20
    city_center = {'lat': 52.516667, 'lon': 13.383333} # Berlin

    def __init__(self, typ=None, storage=None, is_live=False):
        self.storage = storage
        self.is_live = is_live
        self.created = time.time()

        assert typ in self.allowed_types
        self.type = typ
        self.uid = str(uuid.uuid4())
        self.ts = time.time()
        # speed is in meters / sec
        self.speed = random.randrange(10, 50) * km_h_to_m_s
        self.heading = random.random() * 360
        self.lattitude = self.city_center['lat']
        self.longitude = self.city_center['lon']

    def move_sync(self):
        'Update timestamp and move vehicle.'

        assert not self.is_live
        self.ts += self.update_interval
        return self.move()

    async def move_async(self):
        'Update timestamp after waiting and move vehicle.'

        assert self.is_live
        await asyncio.sleep(self.update_interval)
        self.ts = time.time()
        return self.move()

    def move(self):
        'Move vehicle one step, update state and communicate new state.'

        # calculate new destination in lat/lon
        lat, lon, head = self.lattitude, self.longitude, self.heading
        dist = self.speed * self.update_interval
        lat_d, lon_d = destination(lat, lon, head, dist)
        self.lattitude = lat_d
        self.longitude = lon_d

        # calculate new heading, adding a small random amount with slight 
        # clock-wise bias
        self.heading += random.randrange(-50, 100) / 10
        self.heading = self.heading % 360

        # communicate new state
        cc = self.city_center
        if distance(cc['lat'], cc['lon'], self.lattitude, self.longitude) < 50000: 
            if self.storage == 'api':
                self.save_api()
            elif self.storage == 'database':
                self.save_database()
        return self

    def save_api(self):
        'Save current vehicle data to an API POST endpoint.'

        data = dict(
            uid=self.uid,
            type=self.type,
            timestamp=self.ts,
            lattitude=self.lattitude,
            longitude=self.longitude,
            heading=self.heading
        )
        try:
            requests.post(url, data, timeout=10)
        except:
            msg = 'Failed calling POST "%s". Is the server running?' % url
            print(msg)
            sys.exit(0)

    def save_database(self):
        'Save current vehicle state into a database.'

        cursor = conn.cursor()
        cmd = "INSERT INTO traffic VALUES (?, ?, ?, ?, ?, ?)"
        vals = (self.uid, self.type, self.ts, self.longitude, self.lattitude, self.heading)
        cursor.execute(cmd, vals)
        conn.commit()


async def create_traffic(vehicle, dur, loop):
    end_time = loop.time() + dur
    while True:
        if loop.time() >= end_time:
            break
        v = await vehicle.move_async()
        print(v.uid, v.ts, v.lattitude, v.longitude, v.heading)
    return v, None


def async_main(num, dur, typ, storage, live):
    # life
    pool = []
    for i in range(num):
        v = Vehicle(typ=typ, storage=storage, is_live=live)
        pool.append(v)
        print(v.uid, v.ts, v.lattitude, v.longitude, v.heading)
    print('')

    # Create coroutine objects to be executed
    loop = asyncio.get_event_loop()
    tasks = [create_traffic(v, dur, loop) for v in pool]

    # asyncio.wait bundles up all coroutine objects and waits for their
    # completion. This resembles a traditional thread queue join.
    task_bundle = asyncio.wait(tasks)
    # run_until_complete will result a result and a pending set, 
    # we can discard the latter.
    result, _ = loop.run_until_complete(task_bundle)
    loop.close()


def main(num, dur, typ, storage, live):
    # not life
    pool = []
    for i in range(num):
        v = Vehicle(typ=typ, storage=storage, is_live=live)
        pool.append(v)
        print(v.uid, v.ts, v.lattitude, v.longitude, v.heading)
    print('')
    for v in pool:
        while True:
            if v.ts > v.created + dur:
                break
            v.move_sync()
            print(v.uid, v.ts, v.lattitude, v.longitude, v.heading)


if __name__ == '__main__':
    desc = 'Simulate vehicles moving and sending data.'
    parser = argparse.ArgumentParser(description=desc)
    add_arg = parser.add_argument
    add_arg('num', 
        type=int,
        help='Number of vehicles to create.')
    add_arg('dur', 
        type=float,
        help='Duration in seconds to run the simulation.')
    add_arg('--live',
        action='store_true',
        help='Run in real-time mode (waiting for time to pass)')
    add_arg('--store',
        default='database', metavar='MODE',
        help='Data storage mode, either "database" (default) or "api".')
    type_help = 'Vehicle type to use for all vehicles, must be one of: ' \
        '%s (default: "bus").' % ", ".join(Vehicle.allowed_types)
    add_arg('--type',
        default='bus', metavar='TYPE', 
        choices=Vehicle.allowed_types, 
        help=type_help)

    args = parser.parse_args()
    if args.live:
        async_main(args.num, args.dur, args.type, args.store, args.live)
    else:
        main(args.num, args.dur, args.type, args.store, args.live)
