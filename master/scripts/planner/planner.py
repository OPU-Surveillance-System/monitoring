"""
Defines the path planner module.
"""
from sys import path
from simanneal import Annealer
import random
import matplotlib.pyplot as plt
from matplotlib import colors
from tqdm import tqdm
import operator
import copy
path.append("..")

import settings

class Solver:
    """
    Define a super class grouping common methods and attributes of different
    solvers.
    """

    def __init__(self, state, mapper, nb_drone):
        """
        Initialize the solver class
        """

        self.state = state
        self.mapper = copy.deepcopy(mapper)
        self.nb_drone = nb_drone
        self.targets = self.mapper.default_targets
        self.mapped_paths = self.mapper.world
        self.battery_plan = [0 for d in range(self.nb_drone)]
        self.plan = [[] for d in range(self.nb_drone)]
        self.cut_plan = []

    def detail_plan(self):
        """
        Build the detailed path for each drone
        """

        for d in range(self.nb_drone):
            for s in range(1, len(self.state[d])):
                self.plan[d] += self.mapper.paths[(self.state[d][s - 1], self.state[d][s])][0]
            cut_plan = []
            base = self.state[d][0]
            tmp = [base]
            for p in range(1, len(self.plan[d])):
                point = tuple(reversed(self.plan[d][p]))
                tmp.append(point)
                if point == base and len(tmp) > 1:
                    cut_plan.append(tmp)
                    tmp = []
            self.cut_plan.append(cut_plan)

    def check_collision(self):
        """
        Check collision between drone in the planned paths
        """

        print("Checking collision")
        for d1 in tqdm(range(self.nb_drone)):
            for d2 in range(self.nb_drone):
                if d1 == d2:
                    pass
                else:
                    common = list(set(self.plan[d1]).intersection(self.plan[d2]))
                    if common != [] and common != [(125, 65)]:
                        for c in common:
                            if self.plan[d1].index(c) == self.plan[d2].index(c) and c != (125, 65):
                                print("COLLISION AT: ", self.plan[d1].index(c))
                                print(self.plan[d1][self.plan[d1].index(c)], self.plan[d2][self.plan[d2].index(c)])
                        return True
        return False

    def write_plan_by_patrol(self):
        """
        Write the drones' paths on the grid
        """

        for d in range(self.nb_drone):
            for p in range(len(self.cut_plan[d])):
                for c in self.cut_plan[d][p]:
                    self.mapped_paths[c[1]][c[0]] = 3 + p

    def write_plan_by_drone(self):
        """
        Write
        the drones' paths on the grid
        """
        for d in range(self.nb_drone):
            for p in range(len(self.cut_plan[d])):
                for c in self.cut_plan[d][p]:
                    self.mapped_paths[c[1]][c[0]] = 3 + d

    def compute_performance(self):
        """
        Define the objective function
        """

        e = []
        for d in range(self.nb_drone):
            e.append(len(self.cut_plan[d]))

        return e

    def plot_plan(self, method, show=True):
        """
        Plot the environment
        """

        #print("Ploting plan")
        #TODO: Add more color to handle more drones
        cmap = colors.ListedColormap(['white', 'black', 'red', 'orange', 'blue', 'green', 'purple', 'pink', 'yellow', 'brown', 'cyan'])
        #self.write_plan_by_patrol()
        self.write_plan_by_drone()
        plt.imshow(self.mapped_paths, interpolation="none", cmap=cmap)
        save = True
        if show:
            plt.show()
            save = False
        if save:
            plt.savefig('data/plot/plan/' + method + str(settings.X_SIZE) + 'x' + str(settings.Y_SIZE) + '.png', dpi=800)


class SimulatedAnnealingPlanner(Annealer, Solver):
    """
    Define a simulated annealing solver
    """

    def __init__(self, state, mapper, nb_drone):
        """
        Initialize the solver
        """

        Solver.__init__(self, state, mapper, nb_drone)
        #random.shuffle(self.targets)

    def move(self):
        """
        Define the annealing process
        """

        for d in range(self.nb_drone):
            for n in self.targets:
                if self.battery_plan[d] + self.mapper.paths[(self.state[d][len(self.state[d]) - 2], n)][1] + self.mapper.paths[(n, self.state[d][len(self.state[d]) - 1])][1] < settings.MAX_BATTERY_UNIT:
                    self.state[d].insert(len(self.state[d]) - 1, n)
                    self.battery_plan[d] += self.mapper.paths[(self.state[d][len(self.state[d]) - 2], n)][1] + self.mapper.paths[(n, self.state[d][len(self.state[d]) - 1])][1]
                    self.targets.remove(n)
            a = random.randint(1, len(self.state[d]) - 2)
            b = random.randint(1, len(self.state[d]) - 2)
            self.state[d][a], self.state[d][b] = self.state[d][b], self.state[d][a]

    def energy(self):
        """
        Define the objective function
        """

        e = Solver.compute_performance(self)
        e = 1 / e

        return e


class GreedyPlanner(Solver):
    """
    Define a greedy solver
    """

    def __init__(self, state, mapper, nb_drone):
        """
        Initialize the solver
        """

        Solver.__init__(self, state, mapper, nb_drone)

    def find_closest_point(self, point, targets):
        """
        Search the closest point according to the given parameter
        """

        points = [self.mapper.paths[(point, t)] for t in targets if t != point]
        points = sorted(points, key=operator.itemgetter(1))

        return points[0]

    def compute_plan(self):
        """
        Compute the plan by trying to visit all points by distance order and
        by returning to base to recharge the battery when necessary.
        """

        #Remove non reachable targets
        targets = list(self.targets)
        check_targets = {t:[] for t in targets}
        for t in targets:
            for d in range(self.nb_drone):
                if self.mapper.paths[(self.state[d][0], t)][1] + self.mapper.paths[(t, self.state[d][0])][1] > settings.MAX_BATTERY_UNIT:
                    check_targets[t].append(d)
        for t in check_targets:
            if len(check_targets[t]) == self.nb_drone:
                targets.remove(t)
        #Compute plan
        d = 0
        battery = 0
        base = self.state[d][0]
        while len(targets) > 0:
            lp = self.state[d][len(self.state[d]) - 1]
            closest = self.find_closest_point(lp, targets)
            cp = tuple(reversed(closest[0][len(closest[0]) - 1]))
            r_battery = closest[1]
            if battery + r_battery + self.mapper.paths[(cp, base)][1] < settings.MAX_BATTERY_UNIT:
                self.state[d].append(cp)
                battery += r_battery
                targets.remove(cp)
            else:
                self.state[d].append(base)
                battery += self.mapper.paths[(lp, base)][1]
                self.battery_plan[d] += battery
                battery = 0
                d += 1
                if d >= self.nb_drone:
                    d = 0
                base = self.state[d][0]

def get_computed_path(mapper, nb_drone):
    #SIMULATED ANNEALING
    # state = [[mapper.starting_point[d], mapper.starting_point[d]] for d in range(nb_drone)]
    # saplan = SimulatedAnnealingPlanner(state, mapper, nb_drone)
    # saplan.copy_strategy = "slice"
    # saplan.steps = 25000
    # saplan.updates = 100
    # itinerary, energy = saplan.anneal()
    # saplan.detail_plan()
    # #collision = saplan.check_collision()
    # energy = int(1 / energy)
    # energy -= 2 * nb_drone
    # #print("BATTERY", saplan.battery_plan)
    # #print("PLAN", itinerary)
    # #print("NUMBER OF VISITED POINTS", energy)
    # saplan.plot_plan("annealing_", show=False)

    #GREEDY
    state = [[mapper.starting_point[d]] for d in range(nb_drone)]
    gplan = GreedyPlanner(state, mapper, nb_drone)
    gplan.compute_plan()
    gplan.detail_plan()
    gplan.check_collision()
    gplan.plot_plan("greedy_", show=False)
    print("PLAN", gplan.state)
    print("BATTERY", gplan.battery_plan)
    print("NUMBER OF PATROL", gplan.compute_performance())

    #RANDOM


    return 0
