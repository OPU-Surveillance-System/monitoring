from tqdm import tqdm
import pickle
from sys import path
path.append("..")

from solvers.solver import SimulatedAnnealingSolver, RandomSolver
import map_converter as m

STEPS = [2000000, 1000000, 500000, 250000, 12500, 50000, 25000, 12500, 5000, 2500, 1250, 500, 250, 125, 50, 25, 12]
TMAX = [5000, 2500, 1250, 750, 500, 250, 125, 100, 90, 80, 70, 60, 50, 40, 30, 20, 15]
TMIN = [12, 10, 9, 8, 5, 4, 1, 0.9, 0.8, 0.5, 0.4, 0.1, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01]
solutions = {}
state = [(1059, 842), (505, 1214), (400, 1122), (502, 339), (866, 512), (1073, 82), (669, 1202), (32, 1122), (45, 52), (209, 993), (118, 653), (487, 896), (748, 638), (271, 1067), (1576, 567), (683, 316), (1483, 1156), (1448, 634), (303, 1220), (759, 823), (1614, 991), (1387, 174), (1618, 227), (367, 39), (35, 902), (967, 690), (944, 327), (912, 1029), (184, 1205), (779, 1026), (694, 123), (1502, 395)]

nb_drone = 2

fs = open("../../webserver/data/serialization/mapper.pickle", "rb")
mapper = pickle.load(fs)
fs.close()
for s in tqdm(STEPS):
    for tmax in TMAX:
        for tmin in TMIN:
            mean = []
            for i in range(20):
                rplan = RandomSolver(state, mapper, nb_drone)
                rplan.solve()
                saplan = SimulatedAnnealingSolver(rplan.state, mapper, nb_drone)
                saplan.copy_strategy = "slice"
                saplan.steps = s
                saplan.Tmax = tmax
                saplan.Tmin = tmin
                saplan.updates = 0
                itinerary, energy = saplan.solve()
                mean.append(energy)
            mean = sum(mean) / len(mean)
            f = open("memo_min_dist", "a")
            f.write(str(s) + " " + str(tmax) + " " + str(tmin) + " " + str(mean) + "\n")
            f.close()
            solutions[(s, tmax, tmin)] = mean
fs = open("../../webserver/data/serialization/grid_search_min_distance_2.pickle", "wb")
pickle.dump(solutions, fs)
fs.close()
