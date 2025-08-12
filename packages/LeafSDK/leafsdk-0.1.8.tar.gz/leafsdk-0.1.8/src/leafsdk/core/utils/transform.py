# leafsdk/core/utils/transform.py

import math
import numpy as np

EARTH_RADIUS = 6371000

def deg2rad(deg):
    return deg * math.pi / 180

def gps_to_relative_3d(home_lat, home_lon, home_alt, lat, lon, alt):
    lat1 = deg2rad(home_lat)
    lon1 = deg2rad(home_lon)
    lat2 = deg2rad(lat)
    lon2 = deg2rad(lon)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    dy = dlat * EARTH_RADIUS
    dx = dlon * EARTH_RADIUS * math.cos(lat1)
    dz = alt - home_alt
    
    return dx, dy, dz

def wrap_to_pi(angle):
    # Wrap the angle within the range -pi to pi
    angle = np.asarray((angle + math.pi) % (2 * math.pi))
    angle = np.where(angle < 0, angle + 2 * math.pi, angle) - np.pi
    return angle