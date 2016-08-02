from tqdm import tqdm
import pickle
from sys import path
path.append("..")

from solver import SimulatedAnnealingPlanner, RandomPlanner
import map_converter as m

STEPS = [1000000, 900000, 800000, 700000, 500000, 400000, 300000, 200000, 100000, 90000, 80000, 70000, 50000, 40000, 30000, 20000, 10000, 9000, 8000, 7000, 6000, 5000, 4000, 3000, 2000, 1000, 500, 250, 100, 50, 25, 10]
TMAX = [100000, 50000, 25000, 10000, 9000, 8000, 7000, 6000, 5000, 4000, 3000, 2000, 1000, 500, 250, 100]
TMIN = [50, 40, 30, 20, 10, 5, 2, 1, 0.5, 0.25, 0.1, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01]
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
                rplan = RandomPlanner(state, mapper, nb_drone)
                rplan.solve()
                saplan = SimulatedAnnealingPlanner(rplan.state, mapper, nb_drone)
                saplan.copy_strategy = "slice"
                saplan.steps = s
                saplan.Tmax = tmax
                saplan.Tmin = tmin
                saplan.updates = 0
                itinerary, energy = saplan.solve()
                mean.append(energy)
            mean = sum(mean) / len(mean)
            f = open("memo", "a")
            f.write(str(s) + " " + str(tmax) + " " + str(tmin) + " " + str(mean) + "\n")
            f.close()
            solutions[(s, tmax, tmin)] = mean
fs = open("../../webserver/data/serialization/grid_search_min_distance.pickle", "wb")
pickle.dump(solutions, fs)
fs.close()
