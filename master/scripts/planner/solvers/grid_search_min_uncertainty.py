from tqdm import tqdm
import pickle
from sys import path
path.append("..")

#from uncertainty_solver import UncertaintySolver, UncertaintySimulatedAnnealingSolver
import uncertainty_solver as us
import map_converter as m

STEPS = [2000000, 1000000, 500000, 250000, 12500, 50000, 25000, 12500, 5000, 2500, 1250, 500, 250, 125, 50, 25, 12]
TMAX = [5000, 2500, 1250, 750, 500, 250, 125, 100, 90, 80, 70, 60, 50, 40, 30, 20, 15]
TMIN = [12, 10, 9, 8, 5, 4, 1, 0.9, 0.8, 0.5, 0.4, 0.1, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01]
solutions = {}
state = [(113, 128), (4, 112), (132, 105), (108, 64), (62, 42), (4, 140), (22, 150), (45, 4), (83, 150), (86, 15), (37, 152), (49, 140), (97, 128), (93, 79), (133, 10), (85, 39), (63, 151), (180, 79), (120, 86), (94, 102), (14, 81), (201, 123), (60, 112), (185, 144), (33, 133), (117, 40), (26, 124), (196, 70)]
nb_drone = 2

fs = open("../../webserver/data/serialization/mapper.pickle", "rb")
mapper = pickle.load(fs)
fs.close()
for s in tqdm(STEPS):
    for tmax in TMAX:
        for tmin in TMIN:
            mean = []
            for i in range(20):
                rplan = us.UncertaintySolver(state, mapper, nb_drone)
                rplan.solve()
                saplan = us.UncertaintySimulatedAnnealingSolver(rplan.state, mapper, nb_drone)
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
