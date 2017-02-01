import GPy
import GPyOpt
import numpy as np
from sys import path
import pickle
import time
from tqdm import tqdm
from random import shuffle
path.append("..")
path.append("../..")
path.append("../../..")

from uncertainty_battery_solver import UncertaintyBatterySimulatedAnnealingSolver, UncertaintyBatteryRandomSolver
import map_converter as m

fs = open("../../../webserver/data/serialization/mapper.pickle", "rb")
mapper = pickle.load(fs)
fs.close()
state = mapper.default_targets
rplan = UncertaintyBatteryRandomSolver(state, mapper, 2)
saplan = UncertaintyBatterySimulatedAnnealingSolver(rplan.state, mapper, 2, penalizer = 0.2)
rplan.solve()
saplan.state = list(rplan.state)
hist = []
hist_u = []
hist_d = []
for i in tqdm(range(10)):
    shuffle(saplan.state)
    saplan.copy_strategy = "slice"
    saplan.steps = 3000000
    saplan.Tmax = 45.58
    saplan.Tmin = 21.56
    saplan.updates = 0
    itinerary, energy = saplan.solve()
    hist.append(energy)
    hist_u.append(saplan.uncertainty_rate)
    hist_d.append(saplan.battery_consumption)
hist = np.array(hist)
hist_u = np.array(hist_u)
hist_d = np.array(hist_d)
print("COST", "Mean:", np.mean(hist), "Var:", np.var(hist), "Std:", np.std(hist), "Max:", np.max(hist), "Min:", np.min(hist))
print("UNCERTAINTY RATE", "Mean:", np.mean(hist_u), "Var:", np.var(hist_u), "Std:", np.std(hist_u), "Max:", np.max(hist_u), "Min:", np.min(hist_u))
print("BATTERY", "Mean:", np.mean(hist_d), "Var:", np.var(hist_d), "Std:", np.std(hist_d), "Max:", np.max(hist_d), "Min:", np.min(hist_d))
