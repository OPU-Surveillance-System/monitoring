"""
Defines the path planner module.
"""

from sys import path
from simanneal import Annealer

path.append("..")
path.append("solver/")

import settings
from solver.solver import GreedyPlanner, SimulatedAnnealingPlanner, RandomPlanner

def get_computed_path(mapper, nb_drone):
    #Initial solution
    print("START GREEDY")
    state = []
    gplan = GreedyPlanner(state, mapper, nb_drone)
    gplan.solve()
    gplan.detail_plan()
    gplan.plot("greedy", False)
    greedy_collision = gplan.check_collision()
    greedy_perf = gplan.compute_performance()
    gplan.get_battery_plan()
    print("START RANDOM")
    state = list(gplan.state)
    rplan = RandomPlanner(state, mapper, nb_drone)
    rplan.solve()
    rplan.detail_plan()
    rplan.plot("random", False)
    r_collision = rplan.check_collision()
    rplan_perf = rplan.compute_performance()
    rplan.get_battery_plan()
    #Try to optimize by applying simuled annealing
    print("START SIMULATED ANNEALING")
    state = list(rplan.state)
    sa_collision = [1]
    while sa_collision != []:
        saplan = SimulatedAnnealingPlanner(state, mapper, nb_drone)
        saplan.copy_strategy = "slice"
        saplan.steps = 200000
        saplan.Tmax = 2884
        saplan.Tmin = 0.01
        saplan.updates = 100
        itinerary, energy = saplan.solve()
        saplan.detail_plan()
        sa_collision = gplan.check_collision()
        print("COLLISION", sa_collision)
    saplan.plot("simulated_annealing", False)
    saplan_perf = saplan.compute_performance()
    saplan.get_battery_plan()
    print("SA BATTERY PLAN", saplan.battery_plan)
    print("GREEDY STATE", gplan.state)
    print("GREEDY PLAN", gplan.plan)
    #print("GREEDY DETAILED PLAN", gplan.detailed_plan)
    print("GREEDY COLLISION", greedy_collision)
    print("GREEDY PERF", greedy_perf)
    print("GREEDY BATTERY PLAN", gplan.battery_plan)
    print("GREEDY NUMBER OF PATROLS", gplan.get_number_patrols())
    print("RANDOM STATE", rplan.state)
    print("RANDOM PLAN", rplan.plan)
    #print("RANDOM DETAILED PLAN", rplan.detailed_plan)
    print("RANDOM COLLISION", r_collision)
    print("RANDOM PERF", rplan_perf)
    print("RANDOM BATTERY PLAN", rplan.battery_plan)
    print("RANDOM NUMBER OF PATROLS", rplan.get_number_patrols())
    print("SIMULATED ANNEALING STATE", saplan.state)
    print("SIMULATED ANNEALING PLAN", saplan.plan)
    #print("SIMULATED ANNEALING DETAILED PLAN", saplan.detailed_plan)
    print("SIMULATED ANNEALING COLLISION", sa_collision)
    print("SIMULATED ANNEALING PERF", saplan_perf)
    print("SIMULATED ANNEALING BATTERY PLAN", saplan.battery_plan)
    print("SIMULATED ANNEALING NUMBER OF PATROLS", saplan.get_number_patrols())
    converted_plan = saplan.mapper.convert_plan(saplan.detailed_plan, nb_drone)
    patrol_lengths = saplan.get_patrol_lengths()

    return converted_plan, max(saplan.get_number_patrols()), patrol_lengths
