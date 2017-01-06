from sys import path
import pickle
import time
path.append("..")

from solver import SimulatedAnnealingSolver, RandomSolver
import map_converter as m

fs = open("../../webserver/data/serialization/mapper.pickle", "rb")
mapper = pickle.load(fs)
fs.close()
iteration = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 100000, 200000, 500000, 750000, 1000000, 2000000, 3000000, 4000000, 5000000, 6000000, 7000000, 8000000, 9000000, 10000000, 11000000, 12000000, 13000000, 14000000, 15000000, 16000000, 17000000, 18000000, 19000000, 20000000]
state = [(1059, 842), (505, 1214), (400, 1122), (502, 339), (866, 512), (1073, 82), (669, 1202), (32, 1122), (45, 52), (209, 993), (118, 653), (487, 896), (748, 638), (271, 1067), (1576, 567), (683, 316), (1483, 1156), (1448, 634), (303, 1220), (759, 823), (1614, 991), (1387, 174), (1618, 227), (367, 39), (35, 902), (967, 690), (944, 327), (912, 1029), (184, 1205), (779, 1026), (694, 123), (1502, 395)]
nb_drone = 1
rplan = RandomSolver(state, mapper, nb_drone)
saplan = SimulatedAnnealingSolver(rplan.state, mapper, nb_drone)
for it in iteration:
    mean = []
    mean_t = []
    for i in range(10):
        rplan.solve()
        saplan.state = rplan.state
        saplan.copy_strategy = "slice"
        saplan.steps = it
        saplan.Tmax = 400
        saplan.Tmin = 40
        saplan.updates = 0
        t_start = time.time()
        itinerary, energy = saplan.solve()
        t_end = time.time()
        mean.append(energy)
        mean_t.append(t_end - t_start)
    mean = sum(mean) / len(mean)
    mean_t = sum(mean_t) / len (mean_t)
    print("Test it:", it, "avg cost:", mean, "avg time:", mean_t)
    f = open("test_cost_res", "a")
    f.write(str(it) + " " + str(mean) + " " + str(mean_t) + "\n")
    f.close()
