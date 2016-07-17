"""
Defines the path planner module.
"""
from sys import path
from simanneal import Annealer

path.append("..")
path.append("solver/")

import settings
from solver.solver import GreedyPlanner, SimulatedAnnealingPlanner

def get_computed_path(mapper, nb_drone):
    #SIMULATED ANNEALING
    #Initial solution
    state = [[mapper.starting_point[d]] for d in range(nb_drone)]
    gplan = GreedyPlanner(state, mapper, nb_drone)
    gplan.solve()
    print("GPLAN", gplan.state)
    gplan.detail_plan()
    gplan.plot("greedy", False)
    perf = gplan.compute_performance()
    #collision = gplan.check_collision()
    print("BATTERY INIT.", gplan.battery_plan)
    print("NUMBER OF PATROL INIT.", gplan.get_number_patrols())
    #Try to optimize by applying simuled annealing
    state = list(gplan.state)
    saplan = SimulatedAnnealingPlanner(state, mapper, nb_drone)
    saplan.copy_strategy = "slice"
    saplan.steps = 100000
    saplan.updates = 0
    print("START ANNEALING")
    saplan.detail_plan()
    itinerary, energy = saplan.solve()
    saplan.state = list(itinerary)
    saplan.detail_plan()
    print("PLAN", itinerary)
    print("BATTERY", saplan.battery_plan)
    print("NUMBER OF PATROLS", saplan.get_number_patrols())
    saplan.plot("annealing", show=False)
    converted_plan = saplan.mapper.convert_plan(saplan.plan, nb_drone)
    patrol_lengths = saplan.get_patrol_lengths()

    return converted_plan, max(saplan.get_number_patrols()), patrol_lengths
