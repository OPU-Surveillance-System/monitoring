import GPy
import GPyOpt
import numpy as np
from sys import path
import pickle
import time
path.append("..")
path.append("../..")
path.append("../../..")

from uncertainty_battery_solver import UncertaintyBatterySimulatedAnnealingSolver, UncertaintyBatteryRandomSolver
import map_converter as m

def bayesian_optimization_min_uncertainty_battery_simulated_annealing(x):
    fs = open("../../../webserver/data/serialization/mapper.pickle", "rb")
    mapper = pickle.load(fs)
    fs.close()
    nb_drone = 2
    state = [(1059, 842), (505, 1214), (400, 1122), (502, 339), (866, 512), (1073, 82), (669, 1202), (32, 1122), (45, 52), (209, 993), (118, 653), (487, 896), (748, 638), (271, 1067), (1576, 567), (683, 316), (1483, 1156), (1448, 634), (303, 1220), (759, 823), (1614, 991), (1387, 174), (1618, 227), (367, 39), (35, 902), (967, 690), (944, 327), (912, 1029), (184, 1205), (779, 1026), (694, 123), (1502, 395)]
    mean = []
    print(x[:,0], x[:,1], x[:,2])
    for i in range(20):
        rplan = UncertaintyBatteryRandomSolver(state, mapper, nb_drone)
        rplan.solve()
        penalizer = x[:,2]
        saplan = UncertaintyBatterySimulatedAnnealingSolver(rplan.state, mapper, nb_drone, penalizer=penalizer)
        saplan.copy_strategy = "slice"
        saplan.steps = 2000000
        saplan.Tmax = x[:,0]
        saplan.Tmin = x[:,1]
        saplan.updates = 0
        itinerary, energy = saplan.solve()
        mean.append(energy)
    mean = sum(mean) / len(mean)
    mean = np.array(mean)

    return mean.reshape(1, 1)

bounds =[{'name': 'var_2', 'type': 'continuous', 'domain': (15, 10000)},
         {'name': 'var_3', 'type': 'continuous', 'domain': (0.01, 14.9)},
         {'name': 'var_4', 'type': 'continuous', 'domain': (0.001, 1)}]
optimizer = GPyOpt.methods.BayesianOptimization(bayesian_optimization_min_uncertainty_battery_simulated_annealing,
                                              domain = bounds,
                                              model_type = 'GP',
                                              acquisition_type = 'EI',
                                              normalize_Y = True,
                                              verbosity = True)
max_iter = 100
t_start = time.time()
optimizer.run_optimization(max_iter, verbosity = True)
t_end = time.time()
print("Ellapsed time:", t_end - t_start, "seconds")
print("Best value:", optimizer.fx_opt, "at [Tmax, Tmin, Lambda]:", optimizer.x_opt)
optimizer.plot_acquisition()
optimizer.plot_convergence()
