import numpy as np
from sys import path
import pickle
import time
import random
from multiprocessing import Pool
path.append("..")
path.append("../..")
path.append("../../..")

from solver import SimulatedAnnealingSolver, RandomSolver
import map_converter as m

def bayesian_optimization_min_dist_simulated_annealing(x):
    fs = open("../../../webserver/data/serialization/mapper.pickle", "rb")
    mapper = pickle.load(fs)
    fs.close()
    nb_drone = 1
    state = [(1059, 842), (505, 1214), (400, 1122), (502, 339), (866, 512), (1073, 82), (669, 1202), (32, 1122), (45, 52), (209, 993), (118, 653), (487, 896), (748, 638), (271, 1067), (1576, 567), (683, 316), (1483, 1156), (1448, 634), (303, 1220), (759, 823), (1614, 991), (1387, 174), (1618, 227), (367, 39), (35, 902), (967, 690), (944, 327), (912, 1029), (184, 1205), (779, 1026), (694, 123), (1502, 395)]
    rplan = RandomSolver(state, mapper, nb_drone)
    saplan = SimulatedAnnealingSolver(rplan.state, mapper, nb_drone)
    hist = []
    for i in range(5):
        rplan.solve()
        saplan.state = list(rplan.state)
        saplan.copy_strategy = "slice"
        saplan.steps = 500000
        saplan.Tmax = x[0]
        saplan.Tmin = x[1]
        saplan.updates = 0
        itinerary, energy = saplan.solve()
        hist.append(energy)
    mean = sum(hist) / len(hist)
    print("temp:", saplan.Tmax, saplan.Tmin, "f:", mean)

    return mean

bo_time = 1149 + 5848
bo_best = 8408.2
t_start = time.time()
t_end = time.time()
e_time = t_end - t_start
best = 30000
best_tmax = 0
best_tmin = 0
hist_mean = []
hist_temp = []
while (e_time < bo_time) and (best > bo_best):
    temp = []
    for i in range(6):
        tmax = 0
        tmin = 0
        while (tmin >= tmax) or ():
            tmax = random.uniform(0.01, 400)
            tmin = random.uniform(0.01, 400)
        temp.append((tmax, tmin))
    hist_temp += temp
    with Pool(6) as p:
        means = p.map(bayesian_optimization_min_dist_simulated_annealing, temp)
    hist_mean += means
    mean = min(means)
    index = means.index(mean)
    if best > mean:
        best = mean
        best_tmax = temp[index][0]
        best_tmin = temp[index][1]
    t_end = time.time()
    e_time = t_end - t_start
    print(e_time)
print("Best:", best, "tmax", tmax, "tmin", tmin, "ellapsed time:", e_time)
f = open("historic_comparison_time_computation", "a")
for i in range(len(hist_temp)):
    f.write(str(hist_temp[i][0]) + " " + str(hist_temp[i][1]) + " " + str(hist_mean[i]))
f.close()
