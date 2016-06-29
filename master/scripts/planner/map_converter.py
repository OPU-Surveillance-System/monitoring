"""
Convert the GUI's map into a grid.
"""

import utm
import numpy as np
import math
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
from matplotlib import colors
from sys import path
from tqdm import tqdm
import pickle
path.append("..")

import settings
import astar

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

    return x, y #Easting, Northing

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

    return point[0], point[1] #Latitude, Longitude

class Mapper():
    """
    Represent the environment as grids.
    """

    def __init__(self, limits, starting_point, obstacles, default_targets):
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
        self.starting_point = self.latlong_to_index(starting_point)
        self.obstacles = obstacles
        self.default_targets = [self.latlong_to_index(t) for t in default_targets]
        self.default_targets.append(self.starting_point)
        self.world = self.create_world()
<<<<<<< HEAD
=======
        print("Computing shortest paths to default targets...")
        self.paths = {(d1, d2):astar.astar(self.world, tuple(reversed(d1)), tuple(reversed(d2))) for d1 in tqdm(self.default_targets) for d2 in self.default_targets}
        #self.paths = {d:astar.astar(self.world, tuple(reversed(self.starting_point)), tuple(reversed(d))) for d in tqdm(self.default_targets)}
        print("Paths computed")
        for k in self.paths:
            if self.paths[k][0]:
                for c in self.paths[k][0]:
                    self.world[c[0]][c[1]] = 4
        for d in self.default_targets:
            self.world[d[1]][d[0]] = 3
        self.world[self.starting_point[1]][self.starting_point[0]] = 2
        self.plot_world()
>>>>>>> mapToGrid

        #Environment uncertainty
        #self.uncertainty_grid = self.create_uncertainty_grid()

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
        x = int(((x - self.X) / self.Z) * settings.X_SIZE)
        y = int(((self.A - y) / self.C) * settings.Y_SIZE)

        return x, y

    def index_to_latlong(self, point):
        """
        Convert a given world's index (expressed by x and y values) in latitude and longitude values

        Keyword arguments:
        point: point index
        """

        x = point[0]
        y = point[1]
        x = ((x * self.Z) / settings.X_SIZE) + self.X
        y = self.A - ((y * self.C) / settings.Y_SIZE)
        lat, long = project_to_original((x, y))

        return lat, long

    def is_non_admissible(self, point, obs_poly):
        """
        Check if a given point is out of campus limits or is an obstacle
        """

        check = False
        x = point[0]
        y = point[1]
        pnt_poly = Point(x, y)
        for p in obs_poly:
            if pnt_poly.intersects(p) == True:
                check = True
                break

        return check

    def create_world(self):
        """
        Create a grid representing the given environment

        Grid values:
        0: admissible cell
        1: non admissible cell
        """

        print("Creating world...")
        world = np.zeros((settings.Y_SIZE, settings.X_SIZE))
        proj_obs = [[self.latlong_to_index(o) for o in obs] for obs in self.obstacles]
        poly_obs = [Polygon(o) for o in proj_obs]
        for j in tqdm(range(0, settings.Y_SIZE)):
            for i in range(0, settings.X_SIZE):
                if self.is_non_admissible((i, j), poly_obs):
                    world[j][i] = 1
                else:
                    world[j][i] = 0
<<<<<<< HEAD
        x, y = self.latlong_to_index(self.starting_point)
        world[y][x] = 2
        print("World created.")
=======
        print("World created")
>>>>>>> mapToGrid

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

        print("Serialize Mapper...")
        mapper = self
        f = open("data/mapper.pickle", "wb")
        pickle.dump(mapper, f)
        f.close()
        print("Mapper serialized.")

    def plot_world(self):
        """
        Plot the environment
        """

        print("Ploting world")
        cmap = colors.ListedColormap(['white', 'black', 'red', 'orange', 'blue'])
        plt.imshow(self.world, interpolation="none", cmap=cmap)
        plt.show()

    def plot_uncertainty_grid(self):
        """
        Plot the uncertainty level
        """
