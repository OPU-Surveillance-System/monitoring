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
    print("START GREEDY")
    state = [[mapper.starting_point[d]] for d in range(nb_drone)]
    gplan = GreedyPlanner(state, mapper, nb_drone)
    gplan.solve()
    gplan.detail_plan()
    gplan.plot("greedy", False)
    perf = gplan.compute_performance()
    greedy_collision = gplan.check_collision()
    gplan.get_battery_plan()
    #Try to optimize by applying simuled annealing
    state = list(gplan.state)
    sa_collision = [1]
    while sa_collision != []:
        saplan = SimulatedAnnealingPlanner(state, mapper, nb_drone)
        saplan.copy_strategy = "slice"
        saplan.steps = 100000
        saplan.updates = 100
        print("START SIMULATED ANNEALING")
        saplan.detail_plan()
        itinerary, energy = saplan.solve()
        saplan.state = list(itinerary)
        saplan.detail_plan()
        sa_collision = gplan.check_collision()
        print("COLLISION IN PLAN", sa_collision)
    saplan.get_battery_plan()
    saplan.plot("annealing", show=False)
    print("GREEDY PLAN", gplan.state)
    print("GREEDY COLLISION", greedy_collision)
    print("GREEDY NUMBER OF PATROL", gplan.get_number_patrols())
    print("GREEDY BATTERY", gplan.battery_plan)
    print("SIMULATED ANNEALING PLAN", itinerary)
    print("SIMULATED ANNEALING COLLISION", sa_collision)
    print("SIMULATED ANNEALING NUMBER OF PATROLS", saplan.get_number_patrols())
    print("SIMULATED ANNEALING BATTERY", saplan.battery_plan)
    converted_plan = saplan.mapper.convert_plan(saplan.plan, nb_drone)
    patrol_lengths = saplan.get_patrol_lengths()

    return converted_plan, max(saplan.get_number_patrols()), patrol_lengths
