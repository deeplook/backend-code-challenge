"""
Maps to show locations of vehicles.
"""

import os
import time

import matplotlib
import pandas as pd

from utils import bbox


# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')


def make_map_traffic(data):
    import json
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    from mpl_toolkits.basemap import Basemap

    mpl.use('Agg')

    # load points from geojson file
    path = os.path.join(os.getcwd(), 'geo/stops_berlin.geojson')
    js = json.load(open(path))
    lonlats = [f['geometry']['coordinates'] for f in js['features']]

    # compute bounding box (ll, ur)
    class Point(object):
        def __init__(self, **kwargs):
            for k in kwargs:
                setattr(self, k, kwargs[k])
    p = lonlats[0]
    ll = Point(lon=p[0], lat=p[1])
    ur = Point(lon=p[0], lat=p[1])
    for (lon, lat) in lonlats:
        ll.lon = lon if lon < ll.lon else ll.lon
        ll.lat = lat if lat < ll.lat else ll.lat
        ur.lon = lon if lon > ur.lon else ur.lon
        ur.lat = lat if lat > ur.lat else ur.lat

    # create map
    plt.figure(num=1, figsize=(25, 10))
    map = Basemap(projection='mill', resolution='c', \
        llcrnrlat=ll.lat, urcrnrlat=ur.lat, \
        llcrnrlon=ll.lon, urcrnrlon=ur.lon \
        # llcrnrlat=ll.lat-1, urcrnrlat=ur.lat+1, \
        # llcrnrlon=ll.lon-1, urcrnrlon=ur.lon+1 \
    )
    map.drawmapboundary(fill_color='#aaddff')
    map.fillcontinents(color='#dddddd', lake_color='#aaddff')
    map.drawcountries()
    map.drawcoastlines()
    map.readshapefile('geo/berlin/roads', 'berlin')

    for (lat, lon) in data:
        map.plot(lat, lon, 'ro', markersize=10, latlon=True)

    lat, lon = 13.383333, 52.516667
    map.plot(lat, lon, 'bo', markersize=20, latlon=True)

    return plt


# additional, undocumented maps

def make_map_world():
    '''
    Show a simple world map.
    '''

    from mpl_toolkits.basemap import Basemap
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    mpl.use('Agg')
    map = Basemap()
    map.drawcoastlines()
    return plt


def make_map_berlin_bvg():
    import json
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    from mpl_toolkits.basemap import Basemap

    mpl.use('Agg')

    # load points from geojson file
    path = os.path.join(os.getcwd(), 'geo/stops_berlin.geojson')
    js = json.load(open(path))
    lonlats = [f['geometry']['coordinates'] for f in js['features']]

    # compute bounding box (ll, ur)
    class Point(object):
        def __init__(self, **kwargs):
            for k in kwargs:
                setattr(self, k, kwargs[k])
    p = lonlats[0]
    ll = Point(lon=p[0], lat=p[1])
    ur = Point(lon=p[0], lat=p[1])
    for (lon, lat) in lonlats:
        ll.lon = lon if lon < ll.lon else ll.lon
        ll.lat = lat if lat < ll.lat else ll.lat
        ur.lon = lon if lon > ur.lon else ur.lon
        ur.lat = lat if lat > ur.lat else ur.lat

    # create map
    plt.figure(num=1, figsize=(25, 10))
    map = Basemap(projection='mill', resolution='c', \
        llcrnrlat=ll.lat, urcrnrlat=ur.lat, \
        llcrnrlon=ll.lon, urcrnrlon=ur.lon \
    )
    map.drawmapboundary(fill_color='#aaddff')
    map.fillcontinents(color='#dddddd', lake_color='#aaddff')
    map.drawcountries()
    map.drawcoastlines()
    map.readshapefile('geo/berlin/roads', 'berlin')
    for (lon, lat) in lonlats:
        map.plot(lon, lat, 'ro', markersize=3, latlon=True)

    return plt
