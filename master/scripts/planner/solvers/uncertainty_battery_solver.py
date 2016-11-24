"""
Define an abstract solver and a greedy, a random, a simulated annealing solvers
considering an uncertainty grid and penalizing large battery consumption.
"""

import numpy as np
import datetime
import copy
import operator
import random
import math
from sys import path
from simanneal import Annealer
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import cm
path.append("../..")

import settings
from solvers.solver import Solver
from solvers.uncertainty_solver import UncertaintySolver

class UncertaintyBatterySolver(UncertaintySolver):
    """
    Define an abstract class for solvers considering an uncertainty grid and
    penalizing large battery consumption.
    """

    def __init__(self, state, mapper, nb_drone):
        """
        Initialize the abstract solver.

        Keyword arguments:
        state: Initial plan
        mapper: Representation of the environment
        nb_drone: Number of drones
        """

        UncertaintySolver.__init__(self, state, mapper, nb_drone)
        self.uncertainty_rate = 0
        self.battery_consumption = 0

    def compute_performance(self):
        """
        Compute the average uncertainty rate of the points of interest.
        """

        self.estimate_uncertainty_points()
        self.uncertainty_rate = np.mean(np.array(list(self.uncertainty_points.values())))
        self.battery_consumption = self.get_battery_consumption()

        return self.uncertainty_rate * 10000 + settings.PENALIZATION_COEFFICIENT * self.battery_consumption

class UncertaintyBatteryRandomSolver(UncertaintyBatterySolver):
    """
    Define a random solver.
    """

    def __init__(self, state, mapper, nb_drone):
        """
        Initialize the random solver.

        Keyword arguments:
        state: Initial plan
        mapper: Representation of the environment
        nb_drone: Number of drones
        """

        UncertaintyBatterySolver.__init__(self, state, mapper, nb_drone)

    def solve(self):
        """
        Shuffle the order of visit for MAX_RANDOM_PLANNER_ITERATION and return
        the best solution found.
        """

        self.remove_impossible_targets()
        random.shuffle(self.targets)
        best_move = list(self.targets)
        tmp_uncertainty = copy.copy(self.uncertainty_points)
        self.estimate_uncertainty_points()
        best_perf = self.compute_performance()
        self.uncertainty_points = copy.copy(tmp_uncertainty)
        for i in range(settings.MAX_RANDOM_PLANNER_ITERATION):
            random.shuffle(self.state)
            tmp_uncertainty = copy.copy(self.uncertainty_points)
            self.estimate_uncertainty_points()
            perf = self.compute_performance()
            self.uncertainty_points = copy.copy(tmp_uncertainty)
            if perf < best_perf:
                best_move = list(self.state)

        self.state = best_move

class UncertaintyBatterySimulatedAnnealingSolver(Annealer, UncertaintyBatterySolver):
    """
    Define a simulated annealing solver.
    """

    def __init__(self, state, mapper, nb_drone, nb_change=1):
        """
        Initialize the simulated annealing solver.

        Keyword arguments:
        state: Initial plan
        mapper: Representation of the environment
        nb_drone: Number of drones
        nb_change: Number of random permutations (see annealing process)
        """

        UncertaintySolver.__init__(self, state, mapper, nb_drone)
        self.nb_change = nb_change

    def solve(self):
        """
        Launch the annealing process
        """

        self.remove_impossible_targets()
        itinerary, energy = self.anneal()
        self.state = list(itinerary)
        self.compute_performance()

        return self.state, energy

    def move(self):
        """
        Define the annealing process (required by the Annealer class)
        """

        for c in range(self.nb_change):
            a = 0
            b = 0
            while a == b:
                a = random.randint(0, len(self.state) - 1)
                b = random.randint(0, len(self.state) - 1)
            self.state[a], self.state[b] = self.state[b], self.state[a]

    def energy(self):
        """
        Function required by the Annealer class
        """

        e = self.compute_performance()

        return e
