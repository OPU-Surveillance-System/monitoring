import GPy
import GPyOpt
import numpy as np
from sys import path
import pickle
import time
from tqdm import tqdm
path.append("..")
path.append("../..")
path.append("../../..")

from solver import SimulatedAnnealingSolver, RandomSolver
import map_converter as m

fs = open("../../../webserver/data/serialization/mapper.pickle", "rb")
mapper = pickle.load(fs)
fs.close()
nb_drone = 1
state = [(1059, 842), (505, 1214), (400, 1122), (502, 339), (866, 512), (1073, 82), (669, 1202), (32, 1122), (45, 52), (209, 993), (118, 653), (487, 896), (748, 638), (271, 1067), (1576, 567), (683, 316), (1483, 1156), (1448, 634), (303, 1220), (759, 823), (1614, 991), (1387, 174), (1618, 227), (367, 39), (35, 902), (967, 690), (944, 327), (912, 1029), (184, 1205), (779, 1026), (694, 123), (1502, 395)]
rplan = RandomSolver(state, mapper, nb_drone)
saplan = SimulatedAnnealingSolver(rplan.state, mapper, nb_drone)
hist = []
for i in tqdm(range(100)):
    rplan.solve()
    saplan.state = list(rplan.state)
    saplan.copy_strategy = "slice"
    saplan.steps = 10000000
    tmax = 987.57443341
    tmin = 1
    saplan.Tmax = tmax
    saplan.Tmin = tmin
    saplan.updates = 0
    itinerary, energy = saplan.solve()
    hist.append(energy)
hist = np.array(hist)
print("Mean:", np.mean(hist), "Var:", np.var(hist), "Std:", np.std(hist))
print(hist)
