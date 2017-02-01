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

    def __init__(self, state, mapper, nb_drone, penalizer=None):
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
        if penalizer != None:
            self.penalizer = penalizer
        else:
            self.penalizer = settings.PENALIZATION_COEFFICIENT

    def compute_performance(self):
        """
        Compute the average uncertainty rate of the points of interest.
        """

        mean, battery = self.estimate_uncertainty_points()

        return mean, battery

class UncertaintyBatteryRandomSolver(UncertaintyBatterySolver):
    """
    Define a random solver.
    """

    def __init__(self, state, mapper, nb_drone, penalizer=None):
        """
        Initialize the random solver.

        Keyword arguments:
        state: Initial plan
        mapper: Representation of the environment
        nb_drone: Number of drones
        """

        UncertaintyBatterySolver.__init__(self, state, mapper, nb_drone, penalizer)

    def solve(self):
        """
        Shuffle the order of visit for MAX_RANDOM_PLANNER_ITERATION and return
        the best solution found.
        """

        self.remove_impossible_targets()
        random.shuffle(self.targets)
        best_move = list(self.targets)
        mean, battery = self.compute_performance()
        best_perf = 10000 * mean + self.penalizer * battery
        for i in range(settings.MAX_RANDOM_PLANNER_ITERATION):
            random.shuffle(self.state)
            mean, battery = self.compute_performance()
            perf = 10000 * mean + self.penalizer * battery
            if perf < best_perf:
                best_move = list(self.state)

        self.state = best_move

class UncertaintyBatterySimulatedAnnealingSolver(Annealer, UncertaintyBatterySolver):
    """
    Define a simulated annealing solver.
    """

    def __init__(self, state, mapper, nb_drone, nb_change=1, penalizer=None):
        """
        Initialize the simulated annealing solver.

        Keyword arguments:
        state: Initial plan
        mapper: Representation of the environment
        nb_drone: Number of drones
        nb_change: Number of random permutations (see annealing process)
        """

        UncertaintyBatterySolver.__init__(self, state, mapper, nb_drone, penalizer)
        self.nb_change = nb_change

    def solve(self):
        """
        Launch the annealing process
        """

        self.remove_impossible_targets()
        itinerary, energy = self.anneal()
        self.state = list(itinerary)
        mean, battery = self.compute_performance()
        self.uncertainty_rate = mean
        self.battery_consumption = battery

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

        mean, battery = self.compute_performance()
        e = mean * 10000 + self.penalizer * battery

        return e
