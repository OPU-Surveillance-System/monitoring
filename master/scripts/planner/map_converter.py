"""
Convert the GUI's map into a grid.
"""

import utm
import math
from sys import path
path.append("..")

import settings

def latlong_to_index(point):
    """
    Convert a given geographical point (expressed by latitude and longitude values) in a world's index

    Keyword arguments:
    point: point in latitude/longitude
    references: list of references points
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
    references: list of references points
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

def create_world(limits, starting_point, obstacles):
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



class Mapper():
    """
    Represent the environment as grids.
    """

    def create_uncertainty_grid():
        """
        Create a grid that represent the uncertainty about the world
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
        self.world = create_world(self.limits, self.starting_point, self.obstacles)
        self.uncertainty_grid = create_uncertainty_grid()

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

    def plot_uncertainty_grid(self):
        """
        Plot the uncertainty level
        """
