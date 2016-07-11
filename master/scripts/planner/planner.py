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

    def __init__(self, state, mapper):
        """
        Initialize the solver
        """

        self.state = state
        self.mapper = mapper
        self.targets = self.mapper.default_targets
        self.battery_plan = 0

    def move(self):
        """
        Define the annealing process
        """

        random.shuffle(self.targets)
        for n in self.targets:
            if self.battery_plan + self.mapper.paths[(self.state[len(self.state) - 2], n)][1] + self.mapper.paths[(n, self.state[len(self.state) - 1])][1] < settings.MAX_BATTERY_UNIT:
                self.state.insert(len(self.state) - 1, n)
                self.battery_plan += self.mapper.paths[(self.state[len(self.state) - 2], n)][1] + self.mapper.paths[(n, self.state[len(self.state) - 1])][1]
                self.targets.remove(n)
        a = random.randint(1, len(self.state) - 2)
        b = random.randint(1, len(self.state) - 2)
        self.state[a], self.state[b] = self.state[b], self.state[a]

    def energy(self):
        """
        Define the objective function
        """

        e = 1 / len(self.state)

        return e


def get_computed_path(mapper):
    pplan = PatrolPlanner([mapper.starting_point, mapper.starting_point], mapper)
    pplan.steps = 50000
    itinerary = pplan.anneal()
    print(itinerary)
    return 0
