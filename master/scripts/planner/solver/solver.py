"""
Define an abstract solver and a greedy, a simulated annealing solvers.
"""

import copy
import matplotlib.pyplot as plt
from matplotlib import colors
from sys import path
import operator
from simanneal import Annealer
import random
path.append("../..")

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
        self.plan = []

    def remove_impossible_targets(self):
        """
        Remove targets that are too far to be visited from the base.
        """

        check_targets = {t:[] for t in self.targets}
        for t in self.targets:
            for d in range(self.nb_drone):
                if self.mapper.paths[(self.state[d][0], t)][1] + self.mapper.paths[(t, self.state[d][0])][1] > settings.MAX_BATTERY_UNIT:
                    check_targets[t].append(d)
        for t in check_targets:
            if len(check_targets[t]) == self.nb_drone:
                print(t, "is impossible to reach from base.")
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

        path = [[] for d in range(self.nb_drone)]
        self.plan = []
        for d in range(self.nb_drone):
            for s in range(1, len(self.state[d])):
                try:
                    path[d] += self.mapper.paths[(self.state[d][s - 1], self.state[d][s])][0]
                except ValueError:
                    print("No path between points: " + str(self.state[d][s - 1]) + " and " + str(self.state[d][s]))
            base = self.state[d][0]
            tmp = [base]
            plan = []
            for p in range(1, len(path[d])):
                point = tuple(reversed(path[d][p]))
                tmp.append(point)
                if point == base and len(tmp) > 1:
                    plan.append(tmp)
                    tmp = []
            self.plan.append(plan)

    def check_collision(self):
        """
        Check collision between drones in the planned paths.
        """

        collision = []
        for d1 in range(self.nb_drone):
            for d2 in range(self.nb_drone):
                if d1 == d2:
                    pass
                else:
                    common = list(set(self.plan[d1]).intersection(self.plan[d2]))
                    if common != []:
                        for c in common:
                            if self.plan[d1].index(c) == self.plan[d2].index(c):
                                print("collision at: ", self.plan[d1].index(c), ", point (d1, d2)", self.plan[d1][self.plan[d1].index(c)], self.plan[d2][self.plan[d2].index(c)])
                                collision.append([d1, d2, c, self.plan[d1][self.plan[d1].index(c)], self.plan[d2][self.plan[d2].index(c)]])

        return collision

    def compute_performance(self):
        """
        Count the number of patrols (objective function)
        """

        e = []
        for d in range(self.nb_drone):
            e.append(len(self.plan[d]))
        e = max(e)

        return e

    def get_number_patrols(self):
        """
        """

        nb_patrols = [len(self.plan[d]) for d in range(self.nb_drone)]

        return nb_patrols

    def get_patrol_lengths(self):
        """
        Looks the longer patrol for each drone
        """

        nb_patrol = self.compute_performance()
        patrols = [0 for i in range(nb_patrol)]
        for d in range(self.nb_drone):
            patrols[p] = max([len(self.plan[d][p]) for p in range(len(self.plan[d]))])

        return patrols

    def plot(self, method, show=True):
        """
        Plot the determined plan over the environment

        Keyword arguments:
        method: A string precising the methods used to determine the plan
        show: If true -> display the plot, else -> save the plot as an image
        """

        #TODO: Create more markers and colors in order to handle a larger number of drones
        d_markers = ["^", "x", ".", "s", "p", "*", "h", "d"]
        p_colors = ["red", "green", "orange", "cyan", "yellow", "purple", "pink", "blue"]
        obstacles = [[],[]]
        paths = [[],[]]
        targets = [[],[]]
        for j in range(len(self.mapped_paths)):
            for i in range(len(self.mapped_paths[j])):
                if self.mapper.world[j][i] == 1:
                    obstacles[0].append(i)
                    obstacles[1].append(-j)
                elif self.mapper.world[j][i] == 3:
                    targets[0].append(i)
                    targets[1].append(-j)
        plt.scatter(obstacles[0], obstacles[1], color='black', marker=',', s=10)
        plt.scatter(targets[0], targets[1], color='blue', s=40)
        for d in range(self.nb_drone):
            for p in range(len(self.plan[d])):
                x = []
                y = []
                for i in range(len(self.plan[d][p])):
                    if i % 2 == 0:
                        x.append(self.plan[d][p][i][0])
                        y.append(-self.plan[d][p][i][1])
                plt.scatter(x, y, color=p_colors[p], marker=d_markers[d], s=10)
        plt.xlim(0, settings.X_SIZE)
        plt.ylim(-settings.Y_SIZE, 0)
        save = True
        if show:
            plt.show()
            save = False
        if save:
            plt.savefig('data/plot/plan/' + method + "_" + str(self.nb_drone) + "_drones_" + str(settings.X_SIZE) + 'x' + str(settings.Y_SIZE) + '.png', dpi=800)
        plt.clf()


class GreedyPlanner(Solver):
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
        base = self.state[d][0]
        while len(self.targets) > 0:
            last_position = self.state[d][len(self.state[d]) - 1]
            closest = self._find_closest_point(last_position, self.targets)
            closest_point = tuple(reversed(closest[0][len(closest[0]) - 1]))
            required_battery = closest[1]
            if battery + required_battery + self.mapper.paths[(closest_point, base)][1] < settings.MAX_BATTERY_UNIT:
                self.state[d].append(closest_point)
                battery += required_battery
                self.targets.remove(closest_point)
            else:
                self.state[d].append(base)
                battery += self.mapper.paths[(last_position, base)][1]
                self.battery_plan[d] += battery
                battery = 0
                d += 1
                if d >= self.nb_drone:
                    d = 0
                base = self.state[d][0]
        self.state[d].append(base)


class SimulatedAnnealingPlanner(Annealer, Solver):
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
        self.start_points = [mapper.starting_point[d] for d in range(nb_drone)]

    def _flat_state(self):
        """
        Keep only the visit order by removing start/return to base/end points in state
        """

        tmp = []
        for d in range(self.nb_drone):
            start = self.start_points[d]
            while start in self.state[d]:
                self.state[d].remove(start)
            tmp += self.state[d]
        self.state = list(tmp)

    def _unflate_state(self):
        """
        Build patrols by reinserting start/return to base/end points in state
        """

        patrol = [[self.start_points[d]] for d in range(self.nb_drone)]
        i = 0
        d = 0
        battery = 0
        while i < len(self.state):
            last_position = patrol[d][len(patrol[d]) - 1]
            target = self.state[i]
            if battery + self.mapper.paths[(last_position, target)][1] + self.mapper.paths[(target, self.start_points[d])][1] < settings.MAX_BATTERY_UNIT:
                patrol[d].append(target)
                battery += self.mapper.paths[(last_position, target)][1]
                self.battery_plan[d] += battery
                i += 1
            else:
                patrol[d].append(self.start_points[d])
                battery += self.mapper.paths[(target, self.start_points[d])][1]
                self.battery_plan[d] += battery
                battery = 0
                d += 1
                if d >= self.nb_drone:
                    d = 0
            if i >= len(self.state) - 1 and patrol[d][len(patrol[d]) - 1] != self.start_points[d]:
                patrol[d].append(self.start_points[d])
        self.state = list(patrol)

    def solve(self):
        """
        Launch the annealing process
        """

        self._flat_state()
        itinerary, energy = self.anneal()
        self.state = list(itinerary)
        self._unflate_state()

        return self.state, energy

    def move(self):
        """
        Define the annealing process (required by the Annealer class)
        """

        for c in range(self.nb_change):
            a = random.randint(0, len(self.state) - 1)
            b = random.randint(0, len(self.state) - 1)
            self.state[a], self.state[b] = self.state[b], self.state[a]

    def compute_performance(self):
        """
        Count the number of travelled cells (objective function)
        """

        start = self.start_points[0]
        battery = self.mapper.paths[(start, self.state[0])][1]
        for i in range(2, len(self.state)):
            battery += self.mapper.paths[(self.state[i - 1], self.state[i])][1]
        battery += self.mapper.paths[(self.state[len(self.state) - 1], start)][1]

        return battery

    def energy(self):
        """
        Function required by the Annealer class
        """

        e = self.compute_performance()

        return e
