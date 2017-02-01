"""
Convert the GUI's map into a grid.
"""

import utm
import numpy as np
import math
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import cm
from sys import path
from tqdm import tqdm
import pickle
import datetime
import time
import random
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
        Instantiate a Mapper object.
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
        self.starting_point = [self.latlong_to_index(s) for s in starting_point]
        self.obstacles = obstacles
        #self.default_targets = [self.latlong_to_index(t) for t in default_targets]
        self.default_targets = self.get_random_target_points(50)

        for s in self.starting_point:
            self.default_targets.append(s)
        self.world = self.create_world()
        for d in self.default_targets:
            self.world[d[1]][d[0]] = 3
        for s in self.starting_point:
            self.world[s[1]][s[0]] = 2
        print("Computing shortest paths to default targets...")
        self.paths = {(d1, d2):astar.astar(self.world, tuple(reversed(d1)), tuple(reversed(d2))) for d1 in tqdm(self.default_targets) for d2 in self.default_targets if d1 != d2}
        for s in self.starting_point:
            self.default_targets.remove(s)
        #self.default_targets = self.default_targets[:-1] #Removing the starting point from target points list
        print("Paths computed")
        self.mapped_paths = np.copy(self.world)
        for k in self.paths:
           if self.paths[k][0]:
               for c in self.paths[k][0]:
                   self.mapped_paths[c[0]][c[1]] = 4
        for p in self.paths:
            if self.paths[p][1] == 1:
                print(p, self.paths[p])
        #Environment uncertainty
        self.uncertainty_grid = np.ones((settings.Y_SIZE, settings.X_SIZE))
        creation_date = datetime.datetime.now()
        self.last_visit = [[creation_date for x in range(settings.X_SIZE)] for y in range(settings.Y_SIZE)]
        #time.sleep(1)
        #self.update_uncertainty_grid()
        #self.plot_uncertainty_grid()
        self.plot_world_default_targets()

    def get_random_target_points(self, num):
        """
        """
        i = 0
        proj_obs = [[self.latlong_to_index(o) for o in obs] for obs in self.obstacles]
        poly_obs = [Polygon(o) for o in proj_obs]
        random_target_points = []
        while i < num:
            is_inadmissible = True
            while is_inadmissible:
                x = random.randint(0, settings.X_SIZE - 1)
                y = random.randint(0, settings.Y_SIZE - 1)
                if not self.is_non_admissible((x, y), poly_obs):
                    is_inadmissible = False
            random_target_points.append((x, y))
            i += 1

        return random_target_points

    def project_limits(self):
        """
        Represent the environment's limits into the projected space and rectangularize the environment.
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
        Convert a given geographical point (expressed by latitude and longitude values) in a world's index.
        Keyword arguments:
        point: point in latitude/longitude
        """

        x, y = project_to_virtual(point)
        x = int(((x - self.X) / self.Z) * settings.X_SIZE)
        y = int(((self.A - y) / self.C) * settings.Y_SIZE)

        return x, y

    def index_to_latlong(self, point):
        """
        Convert a given world's index (expressed by x and y values) in latitude and longitude values.
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
        Check if a given point is out of campus limits or is an obstacle.
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
        Create a grid representing the given environment.
        Grid values:
        0: admissible cell
        1: non admissible cell
        """

        print("Creating world")
        world = np.zeros((settings.Y_SIZE, settings.X_SIZE))
        proj_obs = [[self.latlong_to_index(o) for o in obs] for obs in self.obstacles]
        poly_obs = [Polygon(o) for o in proj_obs]
        for j in tqdm(range(0, settings.Y_SIZE)):
            for i in range(0, settings.X_SIZE):
                if self.is_non_admissible((i, j), poly_obs):
                    world[j][i] = 1
                else:
                    world[j][i] = 0
        print("World created")

        return world

    def convert_plan(self, plan, nb_drone):
        """
        Convert the given plan's points into latitude/longitude points.
        Keyword arguments:
        plan: A plan of paths
        nb_drone: Number of drones
        """

        converted_plan = list(plan)
        for d in range(nb_drone):
            for p in range(len(plan[d])):
                for pt in range(len(plan[d][p])):
                    converted_plan[d][p][pt] = self.index_to_latlong(plan[d][p][pt])

        return converted_plan

    def update_visit_history(self, visit_list):
        """
        Update the visit's register.
        Keyword arguments:
        visit_list: A dictionnary associating dates of visit to points (index).
        """

        print("Updating visit history")
        for visited_point in visit_list:
            self.last_visit[visited_point[1]][visited_point[0]] = visit_list[visited_point]

    def update_uncertainty_grid(self):
        """
        Update the uncertainty level.
        """

        timeshot = datetime.datetime.now()
        print("Updating uncertainty grid")
        for y in tqdm(range(0, settings.Y_SIZE)):
            for x in range(0, settings.X_SIZE):
                diff = timeshot - self.last_visit[y][x]
                self.uncertainty_grid[y][x] = 1 - math.exp(settings.LAMBDA * diff.seconds)
                #self.uncertainty_grid[y][x] = random.random()
        #self.uncertainty_grid[0][0] = 0.01
        #self.uncertainty_grid[10][10] = 0.39

    def plot_world_default_targets(self, show=True):
        """
        Plot default targets.
        """

        print("Ploting default targets")
        fig, ax = plt.subplots()
        cmap = colors.ListedColormap(['white', 'black', 'red', 'orange'])
        ax.imshow(self.world, interpolation="none", cmap=cmap)
        for t in self.default_targets:
            circle1 = plt.Circle((t[0], t[1]), 10, color='grey')
            ax.add_artist(circle1)
        ax.scatter(self.starting_point[0][0], self.starting_point[0][1], marker="*", s=30)
        save = True
        if show:
            plt.show()
            save = False
        if save:
            #plt.savefig('data/plot/world/map_grid_' + str(settings.X_SIZE) + 'x' + str(settings.Y_SIZE) + '.png', dpi=800)
            plt.savefig('data/plot/world/map_grid_target_points' + str(settings.X_SIZE) + 'x' + str(settings.Y_SIZE) + '.png')

    def plot_world(self, show=True):
        """
        Plot the environment.
        """

        print("Ploting world")
        cmap = colors.ListedColormap(['white', 'black', 'red', 'orange'])
        plt.imshow(self.world, interpolation="none", cmap=cmap)
        save = True
        if show:
            plt.show()
            save = False
        if save:
            #plt.savefig('data/plot/world/map_grid_' + str(settings.X_SIZE) + 'x' + str(settings.Y_SIZE) + '.png', dpi=800)
            plt.savefig('data/plot/world/map_grid_' + str(settings.X_SIZE) + 'x' + str(settings.Y_SIZE) + '.png')

    def plot_paths(self, show=True):
        """
        Plot the environment.
        """

        print("Ploting paths")
        fig, ax = plt.subplots()
        cmap = colors.ListedColormap(['white', 'black', 'red', 'orange', 'blue'])
        cax = ax.imshow(self.mapped_paths, interpolation="none", cmap=cmap)
        for t in self.default_targets:
            circ = plt.Circle((t[0], t[1]), radius=2, color='red')
            ax.add_patch(circ)
        save = True
        if show:
            plt.show()
            save = False
        if save:
            #plt.savefig('data/plot/paths/map_grid_' + str(settings.X_SIZE) + 'x' + str(settings.Y_SIZE) + '.png', dpi=800)
            plt.savefig('data/plot/paths/map_grid_' + str(settings.X_SIZE) + 'x' + str(settings.Y_SIZE) + '.png')

    def plot_uncertainty_grid(self):
        """
        Plot the uncertainty level.
        """

        print("Ploting uncertainty grid")
        i,j = np.unravel_index(self.uncertainty_grid.argmax(), self.uncertainty_grid.shape)
        max_proba = self.uncertainty_grid[i, j]
        i,j = np.unravel_index(self.uncertainty_grid.argmin(), self.uncertainty_grid.shape)
        min_proba = self.uncertainty_grid[i, j]
        middle_proba = max_proba / 2
        fig, ax = plt.subplots()
        cax = ax.imshow(self.uncertainty_grid, interpolation="Nearest", cmap=cm.Greys)
        ax.set_title('Uncertainty Grid')
        cbar = fig.colorbar(cax, ticks=[min_proba, middle_proba, max_proba])
        cbar.ax.set_yticklabels([str(int(min_proba * 100)) + '%', str(int(middle_proba * 100)) + '%', str(int(max_proba * 100)) + '%'])
        plt.show()
