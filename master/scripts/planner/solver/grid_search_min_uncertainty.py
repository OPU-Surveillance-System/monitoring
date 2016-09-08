from tqdm import tqdm
import pickle
from sys import path
path.append("..")

from solvers.uncertainty_solver import UncertaintySolver, UncertaintySimulatedAnnealingSolver
import map_converter as m

STEPS = [2000000, 1000000, 500000, 250000, 12500, 50000, 25000, 12500, 5000, 2500, 1250, 500, 250, 125, 50, 25, 12]
TMAX = [5000, 2500, 1250, 750, 500, 250, 125, 100, 90, 80, 70, 60, 50, 40, 30, 20, 15]
TMIN = [12, 10, 9, 8, 5, 4, 1, 0.9, 0.8, 0.5, 0.4, 0.1, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01]
solutions = {}
state = [(118, 653), (759, 823), (1614, 991), (967, 690), (184, 1205), (303, 1220), (912, 1029), (944, 327), (1502, 395), (1387, 174), (505, 1214), (1059, 842), (487, 896), (683, 316), (32, 1122), (1448, 634), (271, 1067), (779, 1026), (35, 902), (209, 993), (748, 638), (367, 39), (1483, 1156), (1618, 227), (694, 123), (866, 512), (45, 52), (669, 1202), (502, 339), (1073, 82), (1576, 567), (400, 1122)]
nb_drone = 2

fs = open("../../webserver/data/serialization/mapper.pickle", "rb")
mapper = pickle.load(fs)
fs.close()
for s in tqdm(STEPS):
    for tmax in TMAX:
        for tmin in TMIN:
            mean = []
            for i in range(20):
                rplan = UncertaintySolver(state, mapper, nb_drone)
                rplan.solve()
                saplan = UncertaintySimulatedAnnealingSolver(rplan.state, mapper, nb_drone)
                saplan.copy_strategy = "slice"
                saplan.steps = s
                saplan.Tmax = tmax
                saplan.Tmin = tmin
                saplan.updates = 0
                itinerary, energy = saplan.solve()
                mean.append(energy)
            mean = sum(mean) / len(mean)
            f = open("memo_min_uncertainty", "a")
            f.write(str(s) + " " + str(tmax) + " " + str(tmin) + " " + str(mean) + "\n")
            f.close()
            solutions[(s, tmax, tmin)] = mean
fs = open("../../webserver/data/serialization/grid_search_uncertainty.pickle", "wb")
pickle.dump(solutions, fs)
fs.close()
