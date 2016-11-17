from tqdm import tqdm
import pickle
from sys import path
path.append("..")
import numpy as np
import math

from uncertainty_solver import UncertaintySimulatedAnnealingSolver, UncertaintyRandomSolver
import map_converter as m

solutions = {}
state = [(113, 128), (4, 112), (132, 105), (108, 64), (62, 42), (4, 140), (22, 150), (45, 4), (83, 150), (86, 15), (37, 152), (49, 140), (97, 128), (93, 79), (133, 10), (85, 39), (63, 151), (180, 79), (120, 86), (94, 102), (14, 81), (201, 123), (60, 112), (185, 144), (33, 133), (117, 40), (26, 124), (196, 70)]
time = np.linspace(1 * 60, 180 * 60, num=30)
nb_drone = 1

fs = open("../../webserver/data/serialization/mapper.pickle", "rb")
mapper = pickle.load(fs)
fs.close()
for t in tqdm(time):
    mean = []
    lam = math.log(1 - 0.99) / t
    for i in range(20):
        rplan = UncertaintyRandomSolver(state, mapper, nb_drone, lam)
        rplan.solve()
        saplan = UncertaintySimulatedAnnealingSolver(rplan.state, mapper, nb_drone, lam)
        saplan.copy_strategy = "slice"
        saplan.steps = 200000
        saplan.Tmax = 1197
        saplan.Tmin = 0.01
        saplan.updates = 0
        itinerary, energy = saplan.solve()
        mean.append(energy / 10000)
    mean = sum(mean) / len(mean)
    f = open("memo", "a")
    f.write(str(t) + " " + str(mean) + "\n")
    f.close()
    solutions[t] = mean
fs = open("../../webserver/data/serialization/lambda_test.pickle", "wb")
pickle.dump(solutions, fs)
fs.close()
