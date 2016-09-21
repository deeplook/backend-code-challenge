"""
Utilities.
"""

from geographiclib.geodesic import Geodesic

geod = Geodesic.WGS84


def distance(lat1, lon1, lat2, lon2):
    '''
    Distance between two lat/lon positions returned as a float in meters.

    All lattitudes and longitudes are expected in degrees.
    '''

    g = geod.Inverse(lat1, lon1, lat2, lon2)
    return g['s12']


def destination(lat1, lon1, azi_deg, distance_m):
    '''
    Destination for given lat/lon, azimuth and distance, returned as a lat/lon pair.

    Lattitude, longitude and azimuth are expected in degrees, and distance in meters.
    '''

    g = geod.Direct(lat1, lon1, azi_deg, distance_m)
    return g['lat2'], g['lon2']


def bbox(lat, lon, radius):
    '''
    Return corners of a bounding box around given lat/long and radius.

    The result is a tuple of two tuples, representing the lower-left and
    upper-right lat/lon values.
    '''

    lat_n, lon_n = destination(lat, lon, 0, 20000)
    lat_e, lon_e = destination(lat, lon, 90, 20000)
    lat_s, lon_s = destination(lat, lon, 180, 20000)
    lat_w, lon_w = destination(lat, lon, 270, 20000)
    lat_ll, lon_ll = lat_s, lon_w
    lat_ur, lon_ur = lat_n, lon_e
    return (lat_ll, lon_ll), (lat_ur, lon_ur)
