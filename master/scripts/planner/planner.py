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
path.append("..")

import settings


class SimulatedAnnealingPlanner(Annealer):
    """
    """

    def __init__(self, state, mapper, nb_drone):
        self.state = state
        self.mapper = mapper
        self.nb_drone = nb_drone
        self.targets = self.mapper.default_targets
        self.mapped_paths = self.mapper.world
        #random.shuffle(self.targets)
        self.battery_plan = [0 for d in range(self.nb_drone)]
        self.plan = [[] for d in range(self.nb_drone)]

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

        e = 0
        for d in range(self.nb_drone):
            e += len(self.state[d])
        e = 1 / e

        return e

    def detail_plan(self):
        """
        Build the detailed path for each drone
        """

        for d in range(self.nb_drone):
            for s in range(1, len(self.state[d])):
                self.plan[d] += self.mapper.paths[(self.state[d][s - 1], self.state[d][s])][0]

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

    def write_plan(self):
        """
        Write the drones' paths on the grid
        """
        for d in range(self.nb_drone):
            for p in self.plan[d]:
                self.mapped_paths[p[0]][p[1]] = 2 + d

class GreedyPlanner:
    """
    """

    def __init__(self, state, mapper, nb_drone):
        """
        """

        self.state = state
        self.mapper = mapper
        self.nb_drone = nb_drone
        self.targets = mapper.default_targets
        self.mapped_paths = self.mapper.world
        self.battery_plan = [0 for d in range(self.nb_drone)]
        self.plan = [[] for d in range(self.nb_drone)]

    def find_closest_point(self, point):
        """
        """

        points = [self.mapper.paths[(point, t)] for t in self.targets]
        points = sorted(points, key=operator.itemgetter(1))

        return points[0]

    def compute_plan(self):
        """
        """

        for d in range(self.nb_drone):
            while self.battery_plan[d] <= settings.MAX_BATTERY_UNIT:
                closest_target = self.find_closest_point(self.state[d][len(self.state[d]) - 2])
                n = closest_target[0][len(closest_target[0]) - 1]
                n = tuple(reversed(n))
                if self.battery_plan[d] + self.mapper.paths[(self.state[d][len(self.state[d]) - 2], n)][1] + self.mapper.paths[(n, self.state[d][len(self.state[d]) - 1])][1] < settings.MAX_BATTERY_UNIT:
                    self.state[d].insert(len(self.state[d]) - 1, n)
                    self.battery_plan[d] += self.mapper.paths[(self.state[d][len(self.state[d]) - 2], n)][1] + self.mapper.paths[(n, self.state[d][len(self.state[d]) - 1])][1]
                    self.targets.remove(n)
                else:
                    break

    def detail_plan(self):
        """
        Build the detailed path for each drone
        """

        for d in range(self.nb_drone):
            for s in range(1, len(self.state[d])):
                self.plan[d] += self.mapper.paths[(self.state[d][s - 1], self.state[d][s])][0]

    def write_plan(self):
        """
        Write the drones' paths on the grid
        """
        for d in range(self.nb_drone):
            for p in self.plan[d]:
                self.mapped_paths[p[0]][p[1]] = 2 + d

    def energy(self):
        """
        Define the objective function
        """

        e = 0
        for d in range(self.nb_drone):
            e += len(self.state[d])

        return e

def plot_plan(plan, method, show=True):
    """
    Plot the environment
    """

    print("Ploting plan")
    #TODO: Add more color to handle more drones
    cmap = colors.ListedColormap(['white', 'black', 'red', 'orange', 'blue'])
    plt.imshow(plan, interpolation="none", cmap=cmap)
    save = True
    if show:
        plt.show()
        save = False
    if save:
        plt.savefig('data/plot/plan/' + method + str(settings.X_SIZE) + 'x' + str(settings.Y_SIZE) + '.png', dpi=800)


def get_computed_path(mapper, nb_drone):
    #SIMULATED ANNEALING
    state = [[mapper.starting_point, mapper.starting_point] for d in range(nb_drone)]
    saplan = SimulatedAnnealingPlanner(state, mapper, nb_drone)
    saplan.copy_strategy = "slice"
    saplan.steps = 50000
    itinerary, energy = saplan.anneal()
    saplan.detail_plan()
    collision = saplan.check_collision()
    energy = 1 / energy
    print(saplan.battery_plan)
    print(itinerary)
    print(energy)
    saplan.write_plan()
    plot_plan(saplan.mapped_paths, "annealing_", show=False)

    #GREEDY
    state = [[mapper.starting_point, mapper.starting_point] for d in range(nb_drone)]
    gplan = GreedyPlanner(state, mapper, nb_drone)
    gplan.compute_plan()
    gplan.detail_plan()
    gplan.write_plan()
    plot_plan(gplan.mapped_paths, "greedy_", show=False)
    print(gplan.state)
    print(gplan.battery_plan)
    print(gplan.energy())

    #RANDOM


    return 0
