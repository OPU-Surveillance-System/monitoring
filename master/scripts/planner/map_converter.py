"""
Converts the GUI's map into a grid.
"""

import math
import utm
import numpy as np
from numpy.linalg import inv
import matplotlib.pyplot as plt
LIMITS = []

def haversine_distance(p1, p2):
    """
    Computes the haversine distance, in meters, between two points expressed in
    latitude/longitude terms.
    Input:
        * p1: latitude/longitude point
        * p2: latitude/longitude point
    Output:
        * haversine distance between p1 and p2 (float)
    """

    earth_radius = 6371000
    phi_1 = math.radians(p1[0])
    phi_2 = math.radians(p2[0])
    delta_lat = math.radians(p2[0] - p1[0])
    delta_lon = math.radians(p2[1] - p1[1])

    a = (math.sin(delta_lat / 2) ** 2) + math.cos(phi_1) * math.cos(phi_2) * (math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = earth_radius * c

    return d

def get_grid_coordinates(p, angle):
    """
    """

    limits = [[34.55016, 135.50613], [34.5465, 135.50109], [34.54064, 135.50728], [34.54441, 135.5123]]
    lat = []
    lon = []
    for elt in limits:
        lat.append(elt[0])
        lon.append(elt[1])

    J = p[1]
    K = p[0]

    X = limits[1][1]
    Y = limits[3][1]
    #X = min(lon)
    #Y = max(lon)
    Z = Y - X
    A = limits[0][0]
    B = limits[2][0]
    #A = max(lat)
    #B = min(lat)
    C = A - B
    x = ((Y - J) / Z) * 714
    y = ((A - K) / C) * 1000

    rad = angle * (math.pi / 180)

    x2 = x * math.cos(rad) - y * math.sin(rad)
    y2 = x * math.sin(rad) + y * math.cos(rad)

    J = Y - ((Z * x2) / 714)
    K = A - ((C * y2) / 1000)

    a = np.array([[math.cos(rad), -math.sin(rad)], [math.sin(rad), math.cos(rad)]])
    ainv = inv(a)
    pos = np.array([x, y])
    new_pos = a * pos

    s1 = new_pos[0][1]+new_pos[0][0]
    s2 = new_pos[1][1]+new_pos[1][0]
    #print(s1)
    #print(s2)

    return s1, s2
    #print(x)
    #print(y)
    #print("[" + str(K) + ", " + str(J) + "]")



def map_to_grid(limits, starting_point, obstacles):
    """
    Convert the GUI's map, represented by some bounds and obstacles, into an
    array.
    Input:
        * limits: array of four latitude/longitude points
        * starting_point: latitude/longitude point
        * obstacles: array of shapes expressed by latitude/longitude points
    Output:
        * gridmap: array
    """

#g = np.linspace(0, 360, num=360)
#lats = []
#lons = []
#for elt in g:
#    lat, lon = get_grid_coordinates([34.55016, 135.50613], elt)
#    lats.append(lat)
#    lons.append(lon)
#
#plt.plot(lats)
#plt.plot(lons)
#plt.show()
