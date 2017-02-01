"""
Define an abstract solver and a greedy, a random, a simulated annealing solvers.
"""

import copy
import matplotlib.pyplot as plt
from matplotlib import colors
from sys import path
import operator
from simanneal import Annealer
import random
import math
import numpy as np
import GPy
import GPyOpt
from tqdm import tqdm

path.append("../..")

import lehmer
import settings

class Solver:
    """
    Define an abstract class for solvers.
    """

    def __init__(self, state, mapper, nb_drone):
        """
        Initialize the abstract solver.

        Keyword arguments:
        state: Initial plan
        mapper: Representation of the environment
        nb_drone: Number of drones
        """

        self.state = state
        self.mapper = copy.deepcopy(mapper)
        self.nb_drone = nb_drone
        self.targets = list(self.mapper.default_targets)
        self.mapped_paths = copy.copy(self.mapper.world)
        self.battery_plan = [0 for d in range(self.nb_drone)]
        self.plan = [[] for d in range(self.nb_drone)]
        self.detailed_plan = [[] for d in range(self.nb_drone)]
        self.start_points = [mapper.starting_point[d] for d in range(nb_drone)]

    def _build_plan(self):
        """
        Build the non detailed plan (non precise path, just order of visits and
        return to base) for each drone.
        """

        last_position = [self.start_points[d] for d in range(self.nb_drone)]
        d = 0
        start = self.start_points[d]
        self.plan[d].append(start)
        limit = 0
        i = 0
        while i < len(self.state):
            #print("i", "statei", self.state[i], "state", self.state)
            if limit + self.mapper.paths[(last_position[d], self.state[i])][1] + self.mapper.paths[(self.state[i], start)][1] < settings.MAX_BATTERY_UNIT:
                limit += self.mapper.paths[(last_position[d], self.state[i])][1]
                self.plan[d].append(self.state[i])
                last_position[d] = self.state[i]
                i += 1
            else:
                last_position[d] = start
                d += 1
                if d >= self.nb_drone:
                    d = 0
                start = self.start_points[d]
                self.plan[d].append(start)
                limit = 0
        for d in range(self.nb_drone):
            if self.plan[d][len(self.plan[d]) - 1] != self.start_points[d]:
                self.plan[d].append(self.start_points[d])

    def remove_impossible_targets(self):
        """
        Remove targets that are too far to be visited from the base.
        """

        check_targets = {t:[] for t in self.targets}
        for t in self.targets:
            for d in range(self.nb_drone):
                start = self.start_points[d]
                if self.mapper.paths[(start, t)][1] + self.mapper.paths[(t, start)][1] > settings.MAX_BATTERY_UNIT:
                    check_targets[t].append(d)
        for t in check_targets:
            if len(check_targets[t]) == self.nb_drone:
                #print(t, "is impossible to reach from base.")
                self.targets.remove(t)

    def solve(self):
        """
        TO BE REIMPLEMENTED IN CHILD: Solver's method
        """

        return 0

    def detail_plan(self):
        """
        Build the detailed plan for each drone.
        """

        self._build_plan()
        path = [[] for d in range(self.nb_drone)]
        for d in range(self.nb_drone):
            for s in range(1, len(self.plan[d])):
                try:
                    path[d] += self.mapper.paths[(self.plan[d][s - 1], self.plan[d][s])][0]
                except KeyError:
                    print("No path between points: " + str(self.plan[d][s - 1]) + " and " + str(self.plan[d][s]))
            base = self.plan[d][0]
            tmp = [base]
            plan = []
            for p in range(1, len(path[d])):
                point = tuple(reversed(path[d][p]))
                tmp.append(point)
                if point == base and len(tmp) > 1:
                    plan.append(tmp)
                    tmp = []
            self.detailed_plan[d] = list(plan)

    def get_battery_plan(self):
        """
        Estimate the battery consumption for each patrol according to the computed plan.
        """

        self.battery_plan = [[] for d in range(self.nb_drone)]
        last_position = [self.start_points[d] for d in range(self.nb_drone)]
        d = 0
        start = self.start_points[d]
        battery = 0
        i = 0
        limit = 0
        while i < len(self.state):
            if limit + self.mapper.paths[(last_position[d], self.state[i])][1] + self.mapper.paths[(self.state[i], start)][1] < settings.MAX_BATTERY_UNIT:
                limit += self.mapper.paths[(last_position[d], self.state[i])][1]
                last_position[d] = self.state[i]
                i += 1
            else:
                limit += self.mapper.paths[(last_position[d], start)][1]
                self.battery_plan[d].append(limit)
                limit = 0
                last_position[d] = start
                d += 1
                if d >= self.nb_drone:
                    d = 0
                start = self.start_points[d]
        for d in range(self.nb_drone):
            if last_position[d] != self.start_points[d]:
                self.battery_plan[d].append(self.mapper.paths[(last_position[d], start)][1])
        total = 0
        for d in range(self.nb_drone):
            sum_b = sum(self.battery_plan[d])
            total += sum_b
            self.battery_plan[d].append(("Total", sum_b))
        self.battery_plan.append(("Total drones", total))

    def check_collision(self):
        """
        Check collision between drones in the planned paths.
        """

        collision = []
        nb_patrol = max(self.get_number_patrols())
        max_patrol_length = max(self.get_patrol_lengths())
        cpy_plan = copy.deepcopy(self.detailed_plan)
        for d in range(self.nb_drone):
            while len(cpy_plan[d]) < nb_patrol:
                cpy_plan[d].append([])
            for p in range(nb_patrol):
                while len(cpy_plan[d][p]) < max_patrol_length:
                    cpy_plan[d][p].append(self.start_points[d])
        for d1 in range(self.nb_drone):
            for d2 in range(self.nb_drone):
                if d1 == d2:
                    pass
                else:
                    for p in range(nb_patrol):
                        common = list(set(cpy_plan[d1][p]).intersection(cpy_plan[d2][p]))
                        if common != []:
                            for c in common:
                                if cpy_plan[d1][p].index(c) == cpy_plan[d2][p].index(c):
                                    print("collision at: ", cpy_plan[d1][p].index(c), ", (d" + str(d1) + ", d" + str(d2) + ")", cpy_plan[d1][p][cpy_plan[d1][p].index(c)], cpy_plan[d2][p][cpy_plan[d2][p].index(c)])
                                    collision.append([d1, d2, c, cpy_plan[d1][p][cpy_plan[d1][p].index(c)], cpy_plan[d2][p][cpy_plan[d2][p].index(c)]])

        return collision

    def get_battery_consumption(self):
        """
        Count the number of traveled cells (objective function)
        """

        last_position = [self.start_points[d] for d in range(self.nb_drone)]
        d = 0
        start = self.start_points[d]
        battery = 0
        i = 0
        limit = 0
        while i < len(self.state):
            if limit + self.mapper.paths[(last_position[d], self.state[i])][1] + self.mapper.paths[(self.state[i], start)][1] < settings.MAX_BATTERY_UNIT:
                limit += self.mapper.paths[(last_position[d], self.state[i])][1]
                last_position[d] = self.state[i]
                i += 1
            else:
                limit += self.mapper.paths[(last_position[d], start)][1]
                battery += limit
                limit = 0
                last_position[d] = start
                d += 1
                if d >= self.nb_drone:
                    d = 0
                start = self.start_points[d]
        for d in range(self.nb_drone):
            if last_position[d] != self.start_points[d]:
                battery += self.mapper.paths[(last_position[d], start)][1]
        return battery

    def compute_performance(self):

        return self.get_battery_consumption()

    def get_number_patrols(self):
        """
        Count the number for patrols for each drone
        """

        nb_patrols = [len(self.detailed_plan[d]) for d in range(self.nb_drone)]

        return nb_patrols

    def get_patrol_lengths(self):
        """
        Look for the longer patrol for each patrol
        """

        nb_patrol = max(self.get_number_patrols())
        patrol_lengths = [0 for i in range(nb_patrol)]
        for p in range(nb_patrol):
            patrol = [0 for i in range(self.nb_drone)]
            for d in range(self.nb_drone):
                try:
                    patrol[d] = len(self.detailed_plan[d][p])
                except IndexError:
                    patrol[d] = 0
            patrol_lengths[p] = max(patrol)

        return patrol_lengths

    def plot(self, method, show=True):
        """
        Plot the determined plan over the environment

        Keyword arguments:
        method: A string precising the methods used to determine the plan
        show: If true -> display the plot, else -> save the plot as an image
        """

        #TODO: Create more markers and colors in order to handle a larger number of drones
        d_markers = ["^", "x", ".", "s", "p", "*", "h", "d"]
        #p_colors = ["red", "green", "orange", "cyan", "yellow", "purple", "pink", "blue", "indigo", "turquoise", "salmon", "skyblue", "coral", "teal", "olive", "chartreuse", "moccasin", "greenyellow"]
        c = plt.get_cmap("Greys_r")
        r = list(range(c.N))[30::1]
        s = int(len(r) / len(self.detailed_plan[0]))
        r = list(range(c.N))[0::s]
        p_colors = []
        for i in r:
            rgb = c(i)[:3]
            p_colors.append(colors.rgb2hex(rgb))
        obstacles = [[],[]]
        paths = [[],[]]
        targets = [[],[]]
        fig, ax = plt.subplots()
        cmap = colors.ListedColormap(['white', 'black', 'red', 'orange'])
        plt.imshow(self.mapper.world, interpolation="none", cmap=cmap)
        for d in range(self.nb_drone):
            for p in range(len(self.detailed_plan[d])):
                for i in range(len(self.detailed_plan[d][p])):
                    l = list(self.detailed_plan[d][p])[0::30]
                    pos_text = l[int(len(l) / 2)]
                    plt.text(pos_text[0] + 2, pos_text[1], str(p+1))
                    x = []
                    y = []
                    for i in l:
                            x.append(i[0])
                            y.append(i[1])
                    plt.scatter(x, y, color=p_colors[p], marker=d_markers[d], s=10)
        plt.xlim(0, settings.X_SIZE)
        plt.ylim(settings.Y_SIZE, 0)
        save = True
        if show:
            plt.show()
            save = False
        if save:
            #plt.savefig('data/plot/plan/' + str(self.nb_drone) + "_drones_" + method + "_" + str(settings.X_SIZE) + 'x' + str(settings.Y_SIZE) + '.png', dpi=800)
            plt.savefig('data/plot/plan/' + str(self.nb_drone) + "_drones_" + method + "_" + str(settings.X_SIZE) + 'x' + str(settings.Y_SIZE) + '.png')
        plt.clf()

class RandomSolver(Solver):
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

        Solver.__init__(self, state, mapper, nb_drone)

    def solve(self):
        """
        Shuffle the order of visit for MAX_RANDOM_PLANNER_ITERATION and return
        the best solution found.
        """

        self.remove_impossible_targets()
        random.shuffle(self.targets)
        best_move = list(self.targets)
        best_perf = self.compute_performance()
        for i in range(settings.MAX_RANDOM_PLANNER_ITERATION):
            random.shuffle(self.state)
            perf = self.compute_performance()
            if perf < best_perf:
                best_move = list(self.state)

        self.state = best_move

class GreedySolver(Solver):
    """
    Define a greedy solver.
    """

    def __init__(self, state, mapper, nb_drone):
        """
        Initialize the greedy solver.

        Keyword arguments:
        state: Initial plan
        mapper: Representation of the environment
        nb_drone: Number of drones
        """

        Solver.__init__(self, state, mapper, nb_drone)

    def _find_closest_point(self, point, targets):
        """
        Search the closest target according to the given location

        Keyword arguments:
        point: A particular location
        targets: List of target points
        """

        points = [self.mapper.paths[(point, t)] for t in targets if t != point]
        points = sorted(points, key=operator.itemgetter(1))

        return points[0]

    def solve(self):
        """
        Compute the plan by trying to visit all points by distance order
        (ascendant) and by returning to base to recharge the battery when
        necessary.
        """

        self.remove_impossible_targets()
        d = 0
        battery = 0
        base = self.start_points[d]
        last_position = base
        while len(self.targets) > 0:
            closest = self._find_closest_point(last_position, self.targets)
            closest_point = tuple(reversed(closest[0][len(closest[0]) - 1]))
            required_battery = closest[1]
            if battery + required_battery + self.mapper.paths[(closest_point, base)][1] < settings.MAX_BATTERY_UNIT:
                self.state.append(closest_point)
                battery += required_battery
                self.targets.remove(closest_point)
                last_position = closest_point
            else:
                battery += self.mapper.paths[(last_position, base)][1]
                battery = 0
                d += 1
                if d >= self.nb_drone:
                    d = 0
                base = self.start_points[d]
                last_position = base


class SimulatedAnnealingSolver(Annealer, Solver):
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

        Solver.__init__(self, state, mapper, nb_drone)
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

        e = self.compute_performance()

        return e

def evaluation(x, alphabet, state, id_to_loc):
    """
    Evaluate a given permutation.
    """

    id_perm = lehmer.perm_from_int(self.alphabet, int(x[:,0][0]))
    self.state = [self.id_to_loc[i] for i in id_perm]
    e = self.compute_performance()
    print("perm:", int(x[:,0][0]), "cost:", e)

    return e

class BayesianSolver(Solver):
    """
    Define a Bayesian Optimization solver.
    """

    def __init__(self, state, mapper, nb_drone, nb_iteration=100):
        """
        Initialize the Bayesian solver.

        Keyword arguments:
        state: Initial plan
        mapper: Representation of the environment
        nb_drone: Number of drones
        nb_iteration: Number of maximum iteration of the optimizer
        """

        Solver.__init__(self, state, mapper, nb_drone)
        self.nb_iteration = nb_iteration
        a = [(i, sum([i[0]**2, i[1]**2])) for i in self.mapper.default_targets]
        a = sorted(a, key=lambda x: x[1])
        self.id_to_loc = {i+1:a[i][0] for i in range(len(a))}
        self.alphabet = [i for i in range(1, len(a) + 1)]
        #self.bounds = [{'name':'permutation', 'type':'continuous', 'domain':(0, int(math.factorial(len(self.alphabet))))}]
        self.fact = int(math.factorial(len(self.alphabet)))
        self.bounds = [{'name':'permutation', 'type':'continuous', 'domain':(0, 100)}]
        self.optimizer = GPyOpt.methods.BayesianOptimization(self.evaluation,
                                                             domain  = self.bounds,
                                                             model_type = 'GP',
                                                             acquisition_type = 'EI',
                                                             initial_design_numdata=10,
                                                             model_update_interval=1,
                                                             normalize_Y = True,
                                                             evaluator_type='sequential',
                                                             batch_size=1,
                                                             num_cores=1,
                                                             acquisition_jitter=0)
        print("INIT DONE")

    def evaluation(self, x):
        """
        Evaluate a given permutation.
        """

        #sample = int(x[:,0][0])
        sample = int((self.fact * x[:,0][0]) / 100)
        id_perm = lehmer.perm_from_int(self.alphabet, sample)
        self.state = [self.id_to_loc[i] for i in id_perm]
        e = self.compute_performance()
        print("perm:", x[:,0][0], "cost:", e)

        return e

    def solve(self):
        """
        Run the Baysian solver (estimate the best permutation).
        """

        max_iter=self.nb_iteration
        #for i in tqdm(range(max_iter)):
        self.optimizer.run_optimization(max_iter, eps=-1.0, report_file="bayes")
        best_id_perm = lehmer.perm_from_int(self.alphabet, int(self.optimizer.x_opt[0]))
        self.state = [self.id_to_loc[i] for i in best_id_perm]
        energy = self.optimizer.fx_opt
        self.optimizer.plot_acquisition()
        self.optimizer.plot_convergence()

        return self.state, energy[0]
