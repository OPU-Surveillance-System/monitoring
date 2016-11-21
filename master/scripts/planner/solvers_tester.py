"""
Compare the results provided by the different solvers
"""

from tqdm import tqdm
import pickle
from sys import path

path.append("..")
path.append("solvers/")

import settings
from solvers.solver import SimulatedAnnealingSolver, RandomSolver
from solvers.uncertainty_solver import UncertaintySimulatedAnnealingSolver, UncertaintyRandomSolver
from solvers.uncertainty_battery_solver import UncertaintyBatteryRandomSolver, UncertaintyBatterySimulatedAnnealingSolver

fs = open("../webserver/data/serialization/mapper.pickle", "rb")
mapper = pickle.load(fs)
fs.close()
state = [(1059, 842), (505, 1214), (400, 1122), (502, 339), (866, 512), (1073, 82), (669, 1202), (32, 1122), (45, 52), (209, 993), (118, 653), (487, 896), (748, 638), (271, 1067), (1576, 567), (683, 316), (1483, 1156), (1448, 634), (303, 1220), (759, 823), (1614, 991), (1387, 174), (1618, 227), (367, 39), (35, 902), (967, 690), (944, 327), (912, 1029), (184, 1205), (779, 1026), (694, 123), (1502, 395)]
nb_drone = 1
nb_test = 10
print("Testing battery consumption solver")
battery_mean_battery = []
battery_mean_uncertainty = []
battery_mean_patrol = []
battery_best_energy = 20000000
battery_best_patrol = []
for t in tqdm(range(nb_test)):
    battery_rplan = RandomSolver(state, mapper, nb_drone)
    battery_rplan.solve()
    battery_saplan = SimulatedAnnealingSolver(battery_rplan.state, mapper, nb_drone)
    battery_saplan.copy_strategy = "slice"
    battery_saplan.steps = 1000000
    battery_saplan.Tmax = 250
    battery_saplan.Tmin = 1
    battery_saplan.updates = 0
    itinerary, energy = battery_saplan.solve()
    if energy < battery_best_energy:
        battery_best_patrol = itinerary
    battery_mean_battery.append(energy)
    battery_mean_uncertainty.append(UncertaintySimulatedAnnealingSolver(itinerary, mapper, nb_drone).compute_performance())
    battery_saplan.detail_plan()
    battery_mean_patrol.append(battery_saplan.get_number_patrols()[0])
battery_mean_battery = sum(battery_mean_battery) / len(battery_mean_battery)
battery_mean_uncertainty = sum(battery_mean_uncertainty) / len(battery_mean_uncertainty)
battery_mean_patrol = sum(battery_mean_patrol) / len(battery_mean_patrol)

print("Testing uncertainty rate solver")
uncertainty_mean_battery = []
uncertainty_mean_uncertainty = []
uncertainty_mean_patrol = []
uncertainty_best_energy = 20000000
uncertainty_best_patrol = []
for t in tqdm(range(nb_test)):
    uncertainty_rplan = UncertaintyRandomSolver(state, mapper, nb_drone)
    uncertainty_rplan.solve()
    uncertainty_saplan = UncertaintySimulatedAnnealingSolver(uncertainty_rplan.state, mapper, nb_drone)
    uncertainty_saplan.copy_strategy = "slice"
    uncertainty_saplan.steps = 2000000
    uncertainty_saplan.Tmax = 50
    uncertainty_saplan.Tmin = 12
    uncertainty_saplan.updates = 0
    itinerary, energy = uncertainty_saplan.solve()
    if energy < uncertainty_best_energy:
        uncertainty_best_patrol = itinerary
    uncertainty_mean_battery.append(uncertainty_saplan.get_battery_consumption())
    uncertainty_mean_uncertainty.append(uncertainty_saplan.compute_performance())
    uncertainty_saplan.detail_plan()
    uncertainty_mean_patrol.append(uncertainty_saplan.get_number_patrols()[0])
uncertainty_mean_battery = sum(uncertainty_mean_battery) / len(uncertainty_mean_battery)
uncertainty_mean_uncertainty = sum(uncertainty_mean_uncertainty) / len(uncertainty_mean_uncertainty)
uncertainty_mean_patrol = sum(uncertainty_mean_patrol) / len(uncertainty_mean_patrol)

print("Testing uncertainty rate + battery solver")
uncertainty_battery_mean_battery = []
uncertainty_battery_mean_uncertainty = []
uncertainty_battery_mean_patrol = []
uncertainty_battery_best_energy = 20000000
uncertainty_battery_best_patrol = []
for t in tqdm(range(nb_test)):
    uncertainty_battery_rplan = UncertaintyBatteryRandomSolver(state, mapper, nb_drone)
    uncertainty_battery_rplan.solve()
    uncertainty_battery_saplan = UncertaintyBatterySimulatedAnnealingSolver(uncertainty_battery_rplan.state, mapper, nb_drone)
    uncertainty_battery_saplan.copy_strategy = "slice"
    uncertainty_battery_saplan.steps = 2000000
    uncertainty_battery_saplan.Tmax = 50
    uncertainty_battery_saplan.Tmin = 12
    uncertainty_battery_saplan.updates = 0
    itinerary, energy = uncertainty_battery_saplan.solve()
    if energy < uncertainty_battery_best_energy:
        uncertainty_battery_best_patrol = itinerary
    uncertainty_battery_mean_battery.append(uncertainty_battery_saplan.battery_consumption)
    uncertainty_battery_mean_uncertainty.append(uncertainty_battery_saplan.uncertainty_rate)
    uncertainty_battery_saplan.detail_plan()
    uncertainty_battery_mean_patrol.append(uncertainty_battery_saplan.get_number_patrols()[0])
uncertainty_battery_mean_battery = sum(uncertainty_battery_mean_battery) / len(uncertainty_battery_mean_battery)
uncertainty_battery_mean_uncertainty = sum(uncertainty_battery_mean_uncertainty) / len(uncertainty_battery_mean_uncertainty)
uncertainty_battery_mean_patrol = sum(uncertainty_battery_mean_patrol) / len(uncertainty_battery_mean_patrol)

print("TESTER   BATTERY     UNCERTAINTY RATE    #PATROLS")
print("BATTERY", "\t", battery_mean_battery, "\t\t", battery_mean_uncertainty, "\t", battery_mean_patrol)
print("UNCERTAINTY", "\t", uncertainty_mean_battery, "\t\t", uncertainty_mean_uncertainty, "\t", uncertainty_mean_patrol)
print("UNCERTAINTY + BATTERY", "\t", uncertainty_battery_mean_battery, "\t\t", uncertainty_battery_mean_uncertainty, "\t", uncertainty_battery_mean_patrol)
#print("Plot solutions")
#battery_saplan = SimulatedAnnealingSolver(battery_best_patrol, mapper, nb_drone)
#battery_saplan.plot("best_battery_simulated_annealing", False)
#uncertainty_saplan = UncertaintySimulatedAnnealingSolver(uncertainty_best_patrol, mapper, nb_drone)
#uncertainty_saplan.plot("best_uncertainty_simulated_annealing", False)
#uncertainty_battery_saplan = UncertaintyBatterySimulatedAnnealingSolver(uncertainty_battery_best_patrol, mapper, nb_drone)
#uncertainty_battery_saplan.plot("best_uncertainty_battery_simulated_annealing", False)
