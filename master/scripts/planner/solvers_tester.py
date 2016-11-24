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
# print("Testing battery consumption solver")
# battery_mean_battery = []
# battery_mean_uncertainty = []
# battery_mean_patrol = []
# for t in tqdm(range(nb_test)):
#     battery_rplan = RandomSolver(state, mapper, nb_drone)
#     battery_rplan.solve()
#     battery_saplan = SimulatedAnnealingSolver(battery_rplan.state, mapper, nb_drone)
#     battery_saplan.copy_strategy = "slice"
#     battery_saplan.steps = 1000000
#     battery_saplan.Tmax = 250
#     battery_saplan.Tmin = 1
#     battery_saplan.updates = 0
#     itinerary, energy = battery_saplan.solve()
#     battery_mean_battery.append(energy)
#     b = battery_mean_battery[len(battery_mean_battery) - 1]
#     battery_mean_uncertainty.append(UncertaintySimulatedAnnealingSolver(itinerary, mapper, nb_drone).compute_performance())
#     u = battery_mean_uncertainty[len(battery_mean_uncertainty) - 1]
#     battery_saplan.detail_plan()
#     battery_mean_patrol.append(battery_saplan.get_number_patrols()[0])
#     p = battery_mean_patrol[len(battery_mean_patrol) - 1]
#     f = open("memo_tester_battery", "a")
#     f.write(str(b) + " " + str(u) + " " + str(p) + "\n")
#     f.close()
# battery_mean_battery = sum(battery_mean_battery) / len(battery_mean_battery)
# battery_mean_uncertainty = sum(battery_mean_uncertainty) / len(battery_mean_uncertainty)
# battery_mean_patrol = sum(battery_mean_patrol) / len(battery_mean_patrol)
#
# print("Testing uncertainty rate solver")
# uncertainty_mean_battery = []
# uncertainty_mean_uncertainty = []
# uncertainty_mean_patrol = []
# for t in tqdm(range(nb_test)):
#     uncertainty_rplan = UncertaintyRandomSolver(state, mapper, nb_drone)
#     uncertainty_rplan.solve()
#     uncertainty_saplan = UncertaintySimulatedAnnealingSolver(uncertainty_rplan.state, mapper, nb_drone)
#     uncertainty_saplan.copy_strategy = "slice"
#     uncertainty_saplan.steps = 2000000
#     uncertainty_saplan.Tmax = 50
#     uncertainty_saplan.Tmin = 12
#     uncertainty_saplan.updates = 0
#     itinerary, energy = uncertainty_saplan.solve()
#     uncertainty_mean_battery.append(uncertainty_saplan.get_battery_consumption())
#     b = uncertainty_mean_battery[len(uncertainty_mean_battery) - 1]
#     uncertainty_mean_uncertainty.append(uncertainty_saplan.compute_performance())
#     u = uncertainty_mean_uncertainty[len(uncertainty_mean_uncertainty) - 1]
#     uncertainty_saplan.detail_plan()
#     uncertainty_mean_patrol.append(uncertainty_saplan.get_number_patrols()[0])
#     p = uncertainty_mean_patrol[len(uncertainty_mean_patrol) - 1]
#     f = open("memo_tester_uncertainty", "a")
#     f.write(str(b) + " " + str(u) + " " + str(p) + "\n")
#     f.close()
# uncertainty_mean_battery = sum(uncertainty_mean_battery) / len(uncertainty_mean_battery)
# uncertainty_mean_uncertainty = sum(uncertainty_mean_uncertainty) / len(uncertainty_mean_uncertainty)
# uncertainty_mean_patrol = sum(uncertainty_mean_patrol) / len(uncertainty_mean_patrol)

print("Testing uncertainty rate + battery solver")
uncertainty_battery_mean_battery = []
uncertainty_battery_mean_uncertainty = []
uncertainty_battery_mean_patrol = []
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
    uncertainty_battery_mean_battery.append(uncertainty_battery_saplan.battery_consumption)
    b = uncertainty_battery_mean_battery[len(uncertainty_battery_mean_battery) - 1]
    uncertainty_battery_mean_uncertainty.append(uncertainty_battery_saplan.uncertainty_rate)
    u = uncertainty_battery_mean_uncertainty[len(uncertainty_battery_mean_uncertainty) - 1]
    uncertainty_battery_saplan.detail_plan()
    uncertainty_battery_mean_patrol.append(uncertainty_battery_saplan.get_number_patrols()[0])
    p = uncertainty_battery_mean_patrol[len(uncertainty_battery_mean_patrol) -1]
    f = open("memo_tester_uncertainty_battery", "a")
    f.write(str(b) + " " + str(u) + " " + str(p) + "\n")
    f.close()
uncertainty_battery_mean_battery = sum(uncertainty_battery_mean_battery) / len(uncertainty_battery_mean_battery)
uncertainty_battery_mean_uncertainty = sum(uncertainty_battery_mean_uncertainty) / len(uncertainty_battery_mean_uncertainty)
uncertainty_battery_mean_patrol = sum(uncertainty_battery_mean_patrol) / len(uncertainty_battery_mean_patrol)

print("TESTER   BATTERY     UNCERTAINTY RATE    #PATROLS")
#print("BATTERY", "\t", battery_mean_battery, "\t\t", battery_mean_uncertainty, "\t", battery_mean_patrol)
#print("UNCERTAINTY", "\t", uncertainty_mean_battery, "\t\t", uncertainty_mean_uncertainty, "\t", uncertainty_mean_patrol)
print("UNCERTAINTY + BATTERY", "\t", uncertainty_battery_mean_battery, "\t\t", uncertainty_battery_mean_uncertainty, "\t", uncertainty_battery_mean_patrol)
