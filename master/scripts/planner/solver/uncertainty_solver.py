"""
Define an abstract solver and a greedy, a random, a simulated annealing solvers considering an uncertainty grid.
"""

import numpy as np
import datetime
import copy
import operator
import random
import math
from sys import path
from simanneal import Annealer
path.append("../..")

import settings
from solver.solver import Solver

class UncertaintySolver(Solver):
    """
    Define an abstract class for solvers considering an uncertainty grid.
    """

    def __init__(self, state, mapper, nb_drone):
        """
        Initialize the abstract solver.

        Keyword arguments:
        state: Initial plan
        mapper: Representation of the environment
        nb_drone: Number of drones
        """

        Solver.__init__(self, state, mapper, nb_drone)
        #self.uncertainty_grid = copy.copy(self.mapper.uncertainty_grid)
        self.uncertainty_grid = {}

    def compute_performance(self):
        """
        Compute the average probability of the uncertainty grid.
        """

        #average_probability = np.mean(self.uncertainty_grid)
        #print(self.uncertainty_grid.items())
        #print(self.uncertainty_grid.items())
        average_probability = np.mean(np.array(list(self.uncertainty_grid.values())))

        return average_probability

    def estimate_uncertainty_grid(self):
        """
        """

        # point_time = {}
        # self.plan = [[] for d in range(self.nb_drone)]
        # self.detailed_plan = [[] for d in range(self.nb_drone)]
        # self.detail_plan()
        # original_timeshot = datetime.datetime.now()
        # memo_time = []
        # for d in range(self.nb_drone):
        #     timeshot = original_timeshot
        #     for p in range(len(self.detailed_plan[d])):
        #         for point in self.detailed_plan[d][p]:
        #             timeshot += datetime.timedelta(milliseconds = settings.TIMESTEP)
        #             if point in point_time:
        #                 if point_time[point] < timeshot:
        #                     point_time[point] = timeshot
        #             else:
        #                 point_time[point] = timeshot
        #     memo_time.append(timeshot)
        # ref = max(memo_time)
        # for point in point_time:
        #     #diff = self.mapper.last_visit[point[1]][point[0]] - point_time[point]
        #     diff = ref - point_time[point]
        #     self.uncertainty_grid[point[1]][point[0]] = 1 - math.exp(settings.LAMBDA * diff.seconds)
        #     #print(diff.seconds, settings.LAMBDA, self.uncertainty_grid[point[1]][point[0]])
        # self.plan = [[] for d in range(self.nb_drone)]
        # self.detailed_plan = [[] for d in range(self.nb_drone)]

        point_time = {}
        self.plan = [[] for d in range(self.nb_drone)]
        self._build_plan()
        original_timeshot = datetime.datetime.now()
        for d in range(self.nb_drone):
            timeshot = original_timeshot
            for p in range(1, len(self.plan[d])):
                point = self.plan[d][p]
                previous_position = self.plan[d][p - 1]
                number_cells = len(self.mapper.paths[(previous_position, point)][0])
                delta = number_cells * settings.TIMESTEP
                timeshot += datetime.timedelta(seconds = delta)
                if point in point_time:
                    if point_time[point] < timeshot:
                        point_time[point] = timeshot
                else:
                    point_time[point] = timeshot
        ref = max(list(point_time.values()))
        for point in point_time:
            diff = ref - point_time[point]
            self.uncertainty_grid[(point[1], point[0])] = 1 - math.exp(settings.LAMBDA * diff.seconds)
        self.plan = [[] for d in range(self.nb_drone)]

class UncertaintyRandomSolver(UncertaintySolver):
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

        UncertaintySolver.__init__(self, state, mapper, nb_drone)

    def solve(self):
        """

        """

        self.remove_impossible_targets()
        random.shuffle(self.targets)
        best_move = list(self.targets)
        tmp_uncertainty = copy.copy(self.uncertainty_grid)
        self.estimate_uncertainty_grid()
        best_perf = self.compute_performance()
        self.uncertainty_grid = copy.copy(tmp_uncertainty)
        for i in range(settings.MAX_RANDOM_PLANNER_ITERATION):
            random.shuffle(self.state)
            tmp_uncertainty = copy.copy(self.uncertainty_grid)
            self.estimate_uncertainty_grid()
            perf = self.compute_performance()
            self.uncertainty_grid = copy.copy(tmp_uncertainty)
            if perf < best_perf:
                best_move = list(self.state)

        self.state = best_move


class UncertaintyGreedySolver(UncertaintySolver):
    """
    Define a greedy solver considering an uncertainty grid.
    """

    def __init__(self, state, mapper, nb_drone):
        """
        Initialize the greedy solver.

        Keyword arguments:
        state: Initial plan
        mapper: Representation of the environment
        nb_drone: Number of drones
        """

        UncertaintySolver.__init__(self, state, mapper, nb_drone)

    def _get_targets_by_uncertainty(self):
        """
        Sort the targets by uncertainty (descendant).
        """

        uncertainty_targets = [(t, self.mapper.uncertainty_grid[t[1]][t[0]]) for t in self.targets]
        uncertainty_targets = list(reversed(sorted(uncertainty_targets, key=operator.itemgetter(1))))

        return uncertainty_targets

    def solve(self):
        """
        Compute the plan by trying to visit all points by uncertainty order
        (descendant) and by returning to base to recharge the battery when
        necessary.
        """

        self.remove_impossible_targets()
        targets = self._get_targets_by_uncertainty()
        d = 0
        battery = 0
        base = self.start_points[d]
        last_position = base
        i = 0
        while i < len(targets):
            next_path = self.mapper.paths[(last_position, targets[i][0])]
            next_point = tuple(reversed(next_path[0][len(next_path[0]) - 1]))
            required_battery = next_path[1]
            if battery + required_battery + self.mapper.paths[(next_point, base)][1] < settings.MAX_BATTERY_UNIT:
                self.state.append(next_point)
                battery += required_battery
                i += 1
                last_position = next_point
            else:
                battery += self.mapper.paths[(last_position, base)][1]
                battery = 0
                d += 1
                if d >= self.nb_drone:
                    d = 0
                base = self.start_points[d]
                last_position = base

class UncertaintySimulatedAnnealingSolver(Annealer, UncertaintySolver):
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

        tmp_uncertainty = copy.copy(self.uncertainty_grid)
        self.estimate_uncertainty_grid()
        e = self.compute_performance()
        self.uncertainty_grid = copy.copy(tmp_uncertainty)
        e *= 10000

        return e
