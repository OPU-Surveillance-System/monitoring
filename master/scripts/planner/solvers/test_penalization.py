from sys import path
import pickle
path.append("..")

from uncertainty_battery_solver import UncertaintyBatterySimulatedAnnealingSolver, UncertaintyBatteryRandomSolver
import map_converter as m

fs = open("../../webserver/data/serialization/mapper.pickle", "rb")
mapper = pickle.load(fs)
fs.close()
pen = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
state = [(1059, 842), (505, 1214), (400, 1122), (502, 339), (866, 512), (1073, 82), (669, 1202), (32, 1122), (45, 52), (209, 993), (118, 653), (487, 896), (748, 638), (271, 1067), (1576, 567), (683, 316), (1483, 1156), (1448, 634), (303, 1220), (759, 823), (1614, 991), (1387, 174), (1618, 227), (367, 39), (35, 902), (967, 690), (944, 327), (912, 1029), (184, 1205), (779, 1026), (694, 123), (1502, 395)]
nb_drone = 1
rplan = UncertaintyBatteryRandomSolver(state, mapper, nb_drone)
saplan = UncertaintyBatterySimulatedAnnealingSolver(rplan.state, mapper, nb_drone)
for p in pen:
    saplan.penalizer = p
    mean_u = []
    mean_d = []
    for i in range(10):
        rplan.solve()
        saplan.state = rplan.state
        saplan.copy_strategy = "slice"
        saplan.steps = 3000000
        saplan.Tmax = 1000
        saplan.Tmin = 1
        saplan.updates = 0
        itinerary, energy = saplan.solve()
        mean_u.append(saplan.uncertainty_rate)
        mean_d.append(saplan.battery_consumption)
    mean_u = sum(mean_u) / len(mean_u)
    mean_d = sum(mean_d) / len (mean_d)
    print("Test pen:", p, "avg u:", mean_u, "avg d:", mean_d)
    f = open("test_pen", "a")
    f.write(str(p) + " " + str(mean_u) + " " + str(mean_d) + "\n")
    f.close()
