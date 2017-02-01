from sys import path
import pickle
import time
path.append("..")

from uncertainty_battery_solver import UncertaintyBatterySimulatedAnnealingSolver, UncertaintyBatteryRandomSolver
import map_converter as m

fs = open("../../webserver/data/serialization/mapper.pickle", "rb")
mapper = pickle.load(fs)
fs.close()
iteration = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 750000, 1000000, 2000000, 3000000, 4000000, 5000000, 6000000, 7000000, 8000000, 9000000, 10000000, 11000000, 12000000, 13000000, 14000000, 15000000, 16000000, 17000000, 18000000, 19000000, 20000000]
state = mapper.default_targets
nb_drone = 2
rplan = UncertaintyBatteryRandomSolver(state, mapper, nb_drone)
saplan = UncertaintyBatterySimulatedAnnealingSolver(rplan.state, mapper, nb_drone)
for it in iteration:
    mean = []
    mean_t = []
    mean_u = []
    mean_d = []
    for i in range(10):
        rplan.solve()
        saplan.state = rplan.state
        saplan.copy_strategy = "slice"
        saplan.steps = it
        saplan.Tmax = 100
        saplan.Tmin = 1
        saplan.updates = 0
        t_start = time.time()
        itinerary, energy = saplan.solve()
        t_end = time.time()
        mean.append(energy)
        mean_t.append(t_end - t_start)
        mean_u.append(saplan.uncertainty_rate)
        mean_d.append(saplan.battery_consumption)
    mean = sum(mean) / len(mean)
    mean_t = sum(mean_t) / len(mean_t)
    mean_u = sum(mean_u) / len(mean_u)
    mean_d = sum(mean_d) / len(mean_d)
    print("Test it:", it, "avg cost:", mean, "avg time:", mean_t, "avg u:", mean_u, "avg d", mean_d)
    f = open("test_cost_res_uncertaintybattery_50", "a")
    f.write(str(it) + " " + str(mean) + " " + str(mean_t) + " " + str(mean_u) + " " + str(mean_d) + "\n")
    f.close()
