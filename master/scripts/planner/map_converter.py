"""
Convert the GUI's map into a grid.
"""

import utm
import numpy as np
import math
import matplotlib as plt
from sys import path
path.append("..")

import settings

def latlong_to_index(point):
    """
    Convert a given geographical point (expressed by latitude and longitude values) in a world's index

    Keyword arguments:
    point: point in latitude/longitude
    """

    x = settings.REFERENCES[0][1]
    y = settings.REFERENCES[1][1]
    z = y - x
    a = settings.REFERENCES[0][0]
    b = settings.REFERENCES[1][0]
    c = a - b

    index_x = ((y - point[1]) / z) * settings.X_SIZE
    index_x = settings.X_SIZE - int(round(index_x))
    if index_x < 0:
        index_x = 0
    elif index_x > settings.X_SIZE:
        index_x = settings.X_SIZE
    index_y = ((a - point[0]) / c) * settings.Y_SIZE
    index_y = int(round(index_y))
    if index_y < 0:
        index_y = 0
    elif index_y > settings.Y_SIZE:
        index_y = settings.Y_SIZE

    return (index_x, index_y)

def index_to_latlong(point):
    """
    Convert a given world's index (expressed by x and y values) in latitude and longitude values

    Keyword arguments:
    point: point index
    """

    x = settings.REFERENCES[0][1]
    y = settings.REFERENCES[1][1]
    z = y - x
    a = settings.REFERENCES[0][0]
    b = settings.REFERENCES[1][0]
    c = a - b

    latitude = a - ((point[1] * c) / settings.Y_SIZE)
    longitude = y - ((point[0] * z) / settings.X_SIZE)

    return (latitude, longitude)

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

        self.limits = limits
        self.starting_point = starting_point
        self.obstacles = obstacles
        self.world = self.create_world(self.limits, self.starting_point, self.obstacles)
        self.uncertainty_grid = self.create_uncertainty_grid()

    def out_limit_or_obstacle(self, x, y):
        """
        Check if a given point is out of campus limits or an obstacle
        """

        lat, long = index_to_latlong([x, y])
        check = False
        if lat >= self.limits[1][0] and long <= self.limits[0][1]:
            check = True
        elif lat <= self.limits[1][0] and long <= self.limits[2][1]:
            check = True
        elif lat <= self.limits[3][0] and long >= self.limits[2][1]:
            check = True
        elif lat >= self.limits[3][0] and long >= self.limits[0][1]:
            check = True
        point = utm.from_latlon(lat, long)
        for o in self.obstacles:
            if len(o) == 4:
                e1 = utm.from_latlon(o[0][0], o[0][1])
                e2 = utm.from_latlon(o[1][0], o[1][1])
                e3 = utm.from_latlon(o[2][0], o[2][1])
                e4 = utm.from_latlon(o[3][0], o[3][1])
                if point[0] >= e2[0] and point[0] <= e4[0]:
                    if point[1] <= e1[1] and point[1] >= e3[1]:
                        chek = True
            elif len(o) == 3:
                e1 = utm.from_latlon(o[0][0], o[0][1])
                e2 = utm.from_latlon(o[1][0], o[1][1])
                e3 = utm.from_latlon(o[2][0], o[2][1])
                if point[0] >= e2[0] and point[0] <= e3[0]:
                    if point[1] <= e1[1] and point[1] >= e2[1] and point[1] >= e3[1]:
                        chek = True

        return check

    def create_world(self, limits, starting_point, obstacles):
        """
        Create a grid representing the given environment

        Keyword arguments:
        limits: environment boundaries
        starting_point: drones' patrol starting point
        obstacles: array of non admissible zones

        Grid values:
        0: admissible cell
        1: non admissible cell
        2: starting point
        """

        world = np.zeros((settings.X_SIZE, settings.Y_SIZE))
        sx, sy = latlong_to_index(starting_point)
        world[sx][sy] = 2
        for i in range(settings.X_SIZE):
            print("I = " + str(i))
            for j in range(settings.Y_SIZE):
                if i != sx and j != sy:
                    if self.out_limit_or_obstacle(i, j) == True:
                        world[i][j] = 1

        return world

    def update_uncertainty_grid(self):
        """
        Update the uncertainty level
        """

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
                    str += "x"
                elif self.world[i][j] == 2:
                    str += "S"
                else:
                    str += " "
            str += "\n"
        f.write(str)
        f.close()
        print("fin plot")

    def plot_uncertainty_grid(self):
        """
        Plot the uncertainty level
        """
