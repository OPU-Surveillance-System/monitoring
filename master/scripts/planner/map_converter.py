"""
Convert the GUI's map into a grid.
"""

import utm
import numpy as np
import math
from shapely.geometry import Polygon
import matplotlib as plt
from sys import path
path.append("..")

import settings

def project_to_virtual(point):
    """
    Project a given point into a virtual space aligned with east.

    Keyword arguments:
    point: Point expressed by Latitude/Longitude values

    Output expressed by UTM values
    """

    point = utm.from_latlon(point[0], point[1])
    x = math.cos(settings.ANGLE) * (point[0] - settings.RP_UTM[0]) - math.sin(settings.ANGLE) * (point[1] - settings.RP_UTM[1]) + settings.RP_UTM[0]
    y = math.sin(settings.ANGLE) * (point[0] - settings.RP_UTM[0]) + math.cos(settings.ANGLE) * (point[1] - settings.RP_UTM[1]) + settings.RP_UTM[1]

    return (x, y) #Easting, Northing

def project_to_original(point):
    """
    Project a given point into the real space.

    Keyword arguments:
    point: Point expressed by UTM values

    Output expressed by Latitude/Longitude values
    """

    x = math.cos(-settings.ANGLE) * (point[0] - settings.RP_UTM[0]) - math.sin(-settings.ANGLE) * (point[1] - settings.RP_UTM[1]) + settings.RP_UTM[0]
    y = math.sin(-settings.ANGLE) * (point[0] - settings.RP_UTM[0]) + math.cos(-settings.ANGLE) * (point[1] - settings.RP_UTM[1]) + settings.RP_UTM[1]
    point = utm.to_latlon(x, y, 53, "S")

    return (point[0], point[1])

class Mapper():
    """
    Represent the environment as grids.
    """

    def __init__(self, limits, starting_point, obstacles):
        """
        Instantiate a Mapper object

        Keyword arguments:
        limits: environment boundaries
        starting_point: drones' patrol starting point
        obstacles: array of non admissible zones
        """

        #Environment boundaries
        self.limits = limits
        self.projected_limits = self.project_limits()

        #Coefficients for index calculations
        self.X = self.projected_limits[0][0]
        self.Y = self.projected_limits[2][0]
        self.Z = self.Y - self.X
        self.A = self.projected_limits[0][1]
        self.B = self.projected_limits[2][1]
        self.C = self.A - self.B

        #Environment elements
        self.starting_point = starting_point
        self.obstacles = obstacles
        self.world = self.create_world()

        #Environment uncertainty
        #self.uncertainty_grid = self.create_uncertainty_grid()


        # print(self.latlong_to_index(self.projected_limits[0]))
        # print(self.latlong_to_index(self.projected_limits[1]))
        # print(self.latlong_to_index(self.projected_limits[2]))
        # print(self.latlong_to_index(self.projected_limits[3]))
        print(self.latlong_to_index())


    def project_limits(self):
        """
        Represent the environment's limits into the projected space and rectangularize the environment
        """

        #TODO: Find a better way to have a rectangular representation of the map (think security)
        top_left = project_to_virtual(self.limits[0])
        top_left = list(top_left)
        bottom_left = project_to_virtual(self.limits[1])
        bottom_left = list(bottom_left)
        bottom_right = project_to_virtual(self.limits[2])
        bottom_right = list(bottom_right)
        top_right = project_to_virtual(self.limits[3])
        top_right = list(top_right)
        top_right[1] = top_left[1]
        top_right[0] = bottom_right[0]
        bottom_left[0] = top_left[0]
        bottom_left[1] = bottom_right[1]

        return top_left, bottom_left, bottom_right, top_right

    def latlong_to_index(self, point):
        """
        Convert a given geographical point (expressed by latitude and longitude values) in a world's index

        Keyword arguments:
        point: point in latitude/longitude
        """

        x, y = project_to_virtual(point)
        #x = point[0]
        #y = point[1]
        x = int(((x - self.X) / self.Z) * settings.X_SIZE)
        y = int(((self.A - y) / self.C) * settings.Y_SIZE)

        return x, y

    def index_to_latlong(self, point):
        """
        Convert a given world's index (expressed by x and y values) in latitude and longitude values

        Keyword arguments:
        point: point index
        """

        return 0

    def is_non_admissible(self, point):
        """
        Check if a given point is out of campus limits or is an obstacle
        """

        check = False
        x, y = latlong_to_index(point)
        pnt_poly = Polygon([(x, y), (x, y + 1), (x + 1, y), (x + 1, y + 1)])
        obs_poly = []
        for o in self.obstacles:
            obs_poly.append(Polygon(o))
        for p in obs_poly:
            if pnt_poly.intersects(p) == True:
                print("Intersection")
                check = True

        return check

    def create_world(self):
        """
        Create a grid representing the given environment

        Grid values:
        0: admissible cell
        1: non admissible cell
        2: starting point
        """

        world = np.zeros((settings.X_SIZE, settings.Y_SIZE))

        return world

    def update_uncertainty_grid(self):
        """
        Update the uncertainty level
        """

        return []

    def save(self):
        """
        Serialize the Mapper object
        """

    def plot_world(self):
        """
        Plot the environment
        """

        print("debut plot")
        f = open("test", "w")
        str = ""
        for i in range(settings.X_SIZE):
            for j in range(settings.Y_SIZE):
                if self.world[i][j] == 1:
                    str += "X"
                elif self.world[i][j] == 2:
                    str += "S"
                else:
                    str += " "
            str += "\n"
        f.write(str)
        f.close()
        print(str)
        print("fin plot")

    def plot_uncertainty_grid(self):
        """
        Plot the uncertainty level
        """
