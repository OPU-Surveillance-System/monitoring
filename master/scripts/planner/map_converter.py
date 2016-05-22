"""
Converts the GUI's map into a grid.
"""

import math
import utm
import matplotlib.pyplot as plt
import numpy
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

def get_grid_coordinates(p):
    """
    """

    limits = [[34.55016, 135.50613], [34.5465, 135.50109], [34.54064, 135.50728], [34.54441, 135.5123]]
    #rad = 90 * (math.pi / 180)
    rad = -1.5708190297615616
    projected_top_left = utm.from_latlon(34.5465, 135.50109)
    projected_top_right = utm.from_latlon(34.55016, 135.50613)
    projected_bottom_left = utm.from_latlon(34.54064, 135.50728)
    projected_bottom_right = utm.from_latlon(34.54441, 135.5123)
    point = utm.from_latlon(34.54545, 135.50822)

    d = projected_top_right[0] - projected_top_left[0]
    tick_x = d / 10
    x = numpy.arange(projected_top_left[0], projected_top_right[0], step=tick_x)
    d = projected_top_left[1] - projected_bottom_right[1]
    tick_y = d / 10
    y = numpy.arange(projected_bottom_right[1], projected_top_left[1], step=tick_y)
    if point[0] >= projected_top_left[0] and point[0] <= projected_bottom_right[0]:
        if point[1] <= projected_top_right[1] and point[1] >= projected_bottom_left[1]:
            print("ok")
        else:
            print(point[1])
            print(projected_top_right[1])
            print(projected_bottom_left[1])
            print("faux2")
    else:
        print(point[0])
        print(projected_top_left[0])
        print(projected_bottom_right[0])
        print("faux1")
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xticks(x)
    ax.set_yticks(y)
    print(x)
    print(y)
    plt.scatter(projected_top_left[0], projected_top_left[1], color='red')
    plt.scatter(projected_top_right[0], projected_top_right[1], color='red')
    plt.scatter(projected_bottom_right[0], projected_bottom_right[1], color='red')
    plt.scatter(projected_bottom_left[0], projected_bottom_left[1], color='red')
    plt.scatter(point[0], point[1])
    plt.grid()
    plt.show()


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

get_grid_coordinates([34.55016, 135.50613])
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
