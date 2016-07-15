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
import time
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

        #print("Checking collision")
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
                                print("COLLISION AT: ", self.plan[d1].index(c))
                                print(self.plan[d1][self.plan[d1].index(c)], self.plan[d2][self.plan[d2].index(c)])
                                collision.append([d1, d2, c, self.plan[d1][self.plan[d1].index(c)], self.plan[d2][self.plan[d2].index(c)]])

        return collision

    def write_plan_by_patrol(self):
        """
        Write the drones' paths on the grid
        """

        for d in range(self.nb_drone):
            for p in range(len(self.cut_plan[d])):
                for c in self.cut_plan[d][p]:
                    self.mapped_paths[c[1]][c[0]] = 4 + p

    def write_plan_by_drone(self):
        """
        Write
        the drones' paths on the grid
        """
        for d in range(self.nb_drone):
            for p in range(len(self.cut_plan[d])):
                for c in self.cut_plan[d][p]:
                    self.mapped_paths[c[1]][c[0]] = 4 + d

    def compute_performance(self):
        """
        Define the objective function
        """

        e = []
        for d in range(self.nb_drone):
            e.append(len(self.cut_plan[d]))

        return max(e)
        #return sum(e)

    def get_patrol_lengths(self):
        """
        """

        nb_patrol = self.compute_performance()
        patrols = [0 for i in range(nb_patrol)]
        for d in range(self.nb_drone):
            for p in range(len(self.cut_plan[d])):
                if patrols[p] < len(self.cut_plan[d][p]):
                    patrols[p] = len(self.cut_plan[d][p])

        return patrols

    def plot(self, method, show=True):
        """
        Plot the determined plan over the environment
        """

        obstacles = [[],[]]
        paths = [[],[]]
        targets = [[],[]]
        d_markers = ["^", "x", ".", "s", "p", "*", "h", "d"]
        p_colors = ["red", "green", "orange", "cyan", "yellow", "purple", "pink"]
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
            for p in range(len(self.cut_plan[d])):
                x = []
                y = []
                for i in range(len(self.cut_plan[d][p])):
                    if i % 2 == 0:
                        x.append(self.cut_plan[d][p][i][0])
                        y.append(-self.cut_plan[d][p][i][1])
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


class SimulatedAnnealingPlanner(Annealer, Solver):
    """
    Define a simulated annealing solver
    """

    def __init__(self, state, mapper, nb_drone, nb_change=1):
        """
        Initialize the solver
        """

        Solver.__init__(self, state, mapper, nb_drone)
        self.nb_change = nb_change
        self.flatten_state = list(self.state)
        self.start_points = []
        self._flat_state()
        #random.shuffle(self.targets)

    def _flat_state(self):
        """
        Keep only the visit order by removing start/return to base/end points in state
        """

        tmp = []
        for d in range(self.nb_drone):
            start = self.state[d][0]
            self.start_points.append(start)
            while(start in self.flatten_state[d]):
                self.flatten_state[d].remove(start)
            tmp += self.flatten_state[d]
        self.state = list(tmp)
        #print(self.state)

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
                i += 1
            else:
                patrol[d].append(self.start_points[d])
                battery = 0
                d += 1
                if d >= self.nb_drone:
                    d = 0
            if i >= len(self.state) - 1 and patrol[d][len(patrol[d]) - 1] != self.start_points[d]:
                patrol[d].append(self.start_points[d])
        self.state = list(patrol)

    def move(self):
        """
        Define the annealing process
        """

        #Apply random change
        #cpy_state = list(self.state)
        for c in range(self.nb_change):
            a = random.randint(0, len(self.state) - 1)
            b = random.randint(0, len(self.state) - 1)
            self.state[a], self.state[b] = self.state[b], self.state[a]
        #check collision
        # collision = self.check_collision()
        # if collision == []:
        #     self.state = list(cpy_state)

    def energy(self):
        """
        Define the objective function
        """

        # start = self.start_points[0]
        # battery = self.mapper.paths[(start, self.flatten_state[0])][1]
        # nb_patrol = 0
        # for i in range(2, len(self.flatten_state)):
        #     if battery + self.mapper.paths[(self.flatten_state[i - 1], self.flatten_state[i])][1] + self.mapper.paths[(self.flatten_state[i], start)][1] < settings.MAX_BATTERY_UNIT:
        #         battery += self.mapper.paths[(self.flatten_state[i - 1], self.flatten_state[i])][1]
        #     else:
        #         nb_patrol += 1
        #         battery = 0

        # return nb_patrol

        start = self.start_points[0]
        battery = self.mapper.paths[(start, self.state[0])][1]
        for i in range(2, len(self.state)):
            battery += self.mapper.paths[(self.state[i - 1], self.state[i])][1]
        battery += self.mapper.paths[(self.state[len(self.state) - 1], start)][1]
        return battery

    def build_plan(self):
        """
        """

        #print(self.state)
        self._unflate_state()
        #print(self.state)
        self.detail_plan()
        print(self.cut_plan)


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
    #Initial solution
    state = [[mapper.starting_point[d]] for d in range(nb_drone)]
    gplan = GreedyPlanner(state, mapper, nb_drone)
    gplan.compute_plan()
    print("GPLAN", gplan.state)
    gplan.detail_plan()
    #gplan.plot("greedy_", False)
    perf = gplan.compute_performance()
    print("BATTERY INIT.", gplan.battery_plan)
    print("NUMBER OF PATROL INIT.", perf)
    #Try to optimize by applying simuled annealing
    state = list(gplan.state)
    saplan = SimulatedAnnealingPlanner(state, mapper, nb_drone)
    saplan.copy_strategy = "slice"
    saplan.steps = 25000
    saplan.updates = 100
    print("START ANNEALING")
    #saplan.detail_plan()
    itinerary, energy = saplan.anneal()
    #print("PLAN", itinerary)
    #print("NUMBER OF PATROLS", energy)
    saplan.build_plan()
    #print(saplan.cut_plan[2])
    #print(saplan.cut_plan[3])
    saplan.plot("annealing_", show=False)
    # patrol_lengths = saplan.get_patrol_lengths()

    #GREEDY
    # state = [[mapper.starting_point[d]] for d in range(nb_drone)]
    # gplan = GreedyPlanner(state, mapper, nb_drone)
    # gplan.compute_plan()
    # gplan.detail_plan()
    # gplan.check_collision()
    # gplan.plot("greedy_", False)
    # perf = gplan.compute_performance()
    # patrol_lengths = gplan.get_patrol_lengths()
    # print(gplan.state)
    # #print("PLAN", gplan.plan)
    # print("BATTERY", gplan.battery_plan)
    # print("NUMBER OF PATROL", perf)

    #return saplan.cut_plan, energy, patrol_lengths
    return 0, 0, 0
