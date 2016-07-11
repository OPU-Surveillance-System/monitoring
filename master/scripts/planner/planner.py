"""
Defines the path planner module.
"""
from sys import path
from simanneal import Annealer
import random
import matplotlib.pyplot as plt
from matplotlib import colors
path.append("..")

import settings


class PatrolPlanner(Annealer):
    """
    """

    def __init__(self, state, mapper, nb_drone):
        """
        Initialize the solver
        """

        self.state = state
        self.mapper = mapper
        self.nb_drone = nb_drone
        self.targets = self.mapper.default_targets
        self.mapped_paths = self.mapper.world
        #random.shuffle(self.targets)
        self.battery_plan = [0 for d in range(nb_drone)]

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

    def plot_plan(self, show=True):
        """
        Plot the environment
        """

        print("Ploting world")
        for d in range(self.nb_drone):
            for i in range(1, len(self.state[d])):
                path = self.mapper.paths[(self.state[d][i-1], self.state[d][i])][0]
                for p in path:
                    self.mapped_paths[p[0]][p[1]] = 2 + d
        cmap = colors.ListedColormap(['white', 'black', 'red', 'orange', 'blue'])
        plt.imshow(self.mapped_paths, interpolation="none", cmap=cmap)
        save = True
        if show:
            plt.show()
            save = False
        if save:
            plt.savefig('data/plot/plan/annealing_' + str(settings.X_SIZE) + 'x' + str(settings.Y_SIZE) + '.png', dpi=800)


def get_computed_path(mapper, nb_drone):
    state = [[mapper.starting_point, mapper.starting_point] for d in range(nb_drone)]
    pplan = PatrolPlanner(state, mapper, nb_drone)
    pplan.copy_strategy = "slice"
    pplan.steps = 50000
    itinerary, energy = pplan.anneal()
    energy = 1 / energy
    print(pplan.battery_plan)
    print(itinerary)
    print(energy)
    pplan.plot_plan()
    return 0
