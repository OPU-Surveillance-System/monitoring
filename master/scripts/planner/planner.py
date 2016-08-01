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
    #Initial solution
    print("START GREEDY")
    state = []
    gplan = GreedyPlanner(state, mapper, nb_drone)
    gplan.solve()
    print("GREEDY STATE", gplan.state)
    gplan.detail_plan()
    print("GREEDY PLAN", gplan.plan)
    #print("GREEDY DETAILED PLAN", gplan.detailed_plan)
    gplan.plot("greedy", False)
    greedy_collision = gplan.check_collision()
    print("GREEDY COLLISION", greedy_collision)
    perf = gplan.compute_performance()
    print("GREEDY PERF", perf)
    gplan.get_battery_plan()
    print("GREEDY BATTERY PLAN", gplan.battery_plan)
    #Try to optimize by applying simuled annealing
    # print("START SIMULATED ANNEALING")
    # state = list(gplan.state)
    # sa_collision = [1]
    # while sa_collision != []:
    #     saplan = SimulatedAnnealingPlanner(state, mapper, nb_drone)
    #     saplan.copy_strategy = "slice"
    #     saplan.steps = 200000
    #     saplan.Tmax = 10000
    #     saplan.Tmin = 0.01
    #     saplan.updates = 100
    #     saplan.detail_plan()
    #     itinerary, energy = saplan.solve()
    #     print("ITITNATERY", itinerary)
    #     print("ENERGY", energy)
    #     saplan.state = list(itinerary)
    #     print("CHECKCHECK", saplan.compute_performance())
    #     #bat = saplan.compute_performance2(itinerary)
    #     #print("compute_performance2 battery:", bat)
    #     saplan.detail_plan()
    #     sa_collision = gplan.check_collision()
    #     print("COLLISION IN PLAN", sa_collision)
    # saplan.get_battery_plan()
    # saplan.plot("annealing", show=False)
    # print("GREEDY PLAN", gplan.state)
    # print("GREEDY COLLISION", greedy_collision)
    # print("GREEDY NUMBER OF PATROL", gplan.get_number_patrols())
    # print("GREEDY BATTERY", gplan.battery_plan)
    # print("SIMULATED ANNEALING PLAN", saplan.state)
    # print("SIMULATED ANNEALING COLLISION", sa_collision)
    # print("SIMULATED ANNEALING NUMBER OF PATROLS", saplan.get_number_patrols())
    # print("SIMULATED ANNEALING BATTERY", saplan.battery_plan)
    # converted_plan = saplan.mapper.convert_plan(saplan.plan, nb_drone)
    # patrol_lengths = saplan.get_patrol_lengths()
    #
    # return converted_plan, max(saplan.get_number_patrols()), patrol_lengths

    return 0, 0, 0
