"""
Defines the path planner module.
"""
from sys import path
from simanneal import Annealer
import random
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
        self.battery_plan = [0 for d in range(nb_drone)]

    def move(self):
        """
        Define the annealing process
        """

        random.shuffle(self.targets)
        for d in range(self.nb_drone):
            for n in self.targets:
                if self.battery_plan[d] + self.mapper.paths[(self.state[d][len(self.state) - 2], n)][1] + self.mapper.paths[(n, self.state[d][len(self.state) - 1])][1] < settings.MAX_BATTERY_UNIT:
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


def get_computed_path(mapper, nb_drone):
    state = [[mapper.starting_point, mapper.starting_point] for d in range(nb_drone)]
    pplan = PatrolPlanner(state, mapper, nb_drone)
    pplan.steps = 50000
    itinerary = pplan.anneal()
    print(pplan.battery_plan)
    print(itinerary)
    return 0
