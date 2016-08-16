"""
Defines the path planner module.
"""

from sys import path

path.append("..")
path.append("solver/")

import settings
from solver.solver import GreedySolver, SimulatedAnnealingSolver, RandomSolver
from solver.uncertainty_solver import UncertaintyGreedySolver, UncertaintySimulatedAnnealingSolver, UncertaintyRandomSolver

def get_computed_path(mapper, nb_drone):
    #Initial solution
    print("START GREEDY")
    state = []
    gplan = GreedySolver(state, mapper, nb_drone)
    gplan.solve()
    gplan.detail_plan()
    gplan.plot("greedy", False)
    greedy_collision = gplan.check_collision()
    greedy_perf = gplan.compute_performance()
    gplan.get_battery_plan()
    print("START RANDOM")
    state = list(gplan.state)
    rplan = RandomSolver(state, mapper, nb_drone)
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
        saplan = SimulatedAnnealingSolver(state, mapper, nb_drone)
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


    # print("MAPPER UNCERTAINTY GRID")
    # print(mapper.uncertainty_grid)
    print("START UNCERTAINTY GREEDY")
    state = []
    gplan = UncertaintyGreedySolver(state, mapper, nb_drone)
    gplan.solve()
    gplan.detail_plan()
    gplan.plot("uncertainty_greedy", False)
    greedy_collision = gplan.check_collision()
    gplan.estimate_uncertainty_grid()
    greedy_perf = gplan.compute_performance()
    gplan.get_battery_plan()
    mapper.uncertainty_grid = gplan.uncertainty_grid
    mapper.plot_uncertainty_grid()
    print("START UNCERTAINTY RANDOM")
    state = list(gplan.state)
    rplan = UncertaintyRandomSolver(state, mapper, nb_drone)
    rplan.solve()
    rplan.detail_plan()
    rplan.plot("uncertainty_random", False)
    r_collision = rplan.check_collision()
    rplan.estimate_uncertainty_grid()
    rplan_perf = rplan.compute_performance()
    rplan.get_battery_plan()
    # print("START UNCERTAINTY SIMULATED ANNEALING")
    # state = list(rplan.state)
    # sa_collision = [1]
    # while sa_collision != []:
    #     saplan = UncertaintySimulatedAnnealingSolver(state, mapper, nb_drone)
    #     saplan.copy_strategy = "slice"
    #     saplan.steps = 200000
    #     saplan.Tmax = 2884
    #     saplan.Tmin = 0.01
    #     saplan.updates = 100
    #     itinerary, energy = saplan.solve()
    #     saplan.detail_plan()
    #     sa_collision = gplan.check_collision()
    #     print("COLLISION", sa_collision)
    # saplan.plot("uncertainty_simulated_annealing", False)
    # saplan_perf = saplan.compute_performance()
    # saplan.get_battery_plan()
    # print("MAPPER UNCERTAINTY GRID")
    # print(mapper.uncertainty_grid)
    # print("GPLAN UNCERTAINTY GRID")
    # print(gplan.uncertainty_grid)
    # print("RPLAN UNCERTAINTY GRID")
    # print(rplan.uncertainty_grid)
    print("UNCERTAINTY GREEDY STATE", gplan.state)
    print("UNCERTAINTY GREEDY PLAN", gplan.plan)
    print("UNCERTAINTY GREEDY COLLISION", greedy_collision)
    print("UNCERTAINTY GREEDY PERF", greedy_perf)
    print("UNCERTAINTY GREEDY BATTERY PLAN", gplan.battery_plan)
    print("UNCERTAINTY GREEDY NUMBER OF PATROLS", gplan.get_number_patrols())
    print("UNCERTAINTY RANDOM STATE", rplan.state)
    print("UNCERTAINTY RANDOM PLAN", rplan.plan)
    print("UNCERTAINTY RANDOM COLLISION", r_collision)
    print("UNCERTAINTY RANDOM PERF", rplan_perf)
    print("UNCERTAINTY RANDOM BATTERY PLAN", rplan.battery_plan)
    print("UNCERTAINTY RANDOM NUMBER OF PATROLS", rplan.get_number_patrols())
    # print("SIMULATED ANNEALING STATE", saplan.state)
    # print("SIMULATED ANNEALING PLAN", saplan.plan)
    # print("SIMULATED ANNEALING COLLISION", sa_collision)
    # print("SIMULATED ANNEALING PERF", saplan_perf)
    # print("SIMULATED ANNEALING BATTERY PLAN", saplan.battery_plan)
    # print("SIMULATED ANNEALING NUMBER OF PATROLS", saplan.get_number_patrols())
    return converted_plan, max(saplan.get_number_patrols()), patrol_lengths
