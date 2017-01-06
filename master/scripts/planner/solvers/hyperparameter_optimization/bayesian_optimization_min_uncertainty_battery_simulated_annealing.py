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
    nb_drone = 1
    rplan = UncertaintyBatteryRandomSolver(state, mapper, nb_drone)
    saplan = UncertaintyBatterySimulatedAnnealingSolver(rplan.state, mapper, nb_drone, penalizer=0.1)
    state = [(1059, 842), (505, 1214), (400, 1122), (502, 339), (866, 512), (1073, 82), (669, 1202), (32, 1122), (45, 52), (209, 993), (118, 653), (487, 896), (748, 638), (271, 1067), (1576, 567), (683, 316), (1483, 1156), (1448, 634), (303, 1220), (759, 823), (1614, 991), (1387, 174), (1618, 227), (367, 39), (35, 902), (967, 690), (944, 327), (912, 1029), (184, 1205), (779, 1026), (694, 123), (1502, 395)]
    hist = []
    for i in range(1):
        rplan.solve()
        saplan.state = list(rplan)
        saplan.copy_strategy = "slice"
        #saplan.steps = 5000000
        saplan.steps = 100
        tmax = x[0,0] * 5000
        tmin = x[0,1] * 5000
        saplan.Tmax = tmax
        saplan.Tmin = tmin
        saplan.updates = 0
        itinerary, energy = saplan.solve()
        hist.append(energy)
    mean = sum(hist) / len(hist)
    cost = np.array([float(mean)])
    print("x:", x, "temp:", tmax, tmin, "f:", cost)
    return cost.reshape(1, 1)

print("Initialization")
domain =[{'name': 'tmax', 'type': 'continuous', 'domain': (0.01, 1)},
         {'name': 'tmin', 'type': 'continuous', 'domain': (0.01, 1)}]
constrains = [{'name': 'constraint', 'constrain': 'x[:,1] - x[:,0]'}]
t_start_init = time.time()
optimizer = GPyOpt.methods.BayesianOptimization(f=bayesian_optimization_min_uncertainty_battery_simulated_annealing,
                                            domain = domain,
                                            constrains = constrains,
                                            model_type = "GP",
                                            acquisition_type = 'EI',
                                            normalize_Y = True,
                                            initial_design_numdata = 6,
                                            evaluator_type = 'random',
                                            batch_size = 6,
                                            num_cores = 6)
t_end_init = time.time()
print("Prior ellapsed time:", t_end_init - t_start_init, "seconds")
optimizer.plot_acquisition(filename="/home/scom/pictures/bayesian_optimization/prior_acquisition_iteration%.03i.png" % (0))
n_iter = 20
print("Start optimization")
t_start = time.time()
for i in range(n_iter):
    optimizer.run_optimization(max_iter=1)
    optimizer.plot_acquisition(filename="/home/scom/pictures/bayesian_optimization/posterior_acquisition_iteration%.03i.png" % (i+1))
t_end = time.time()
print("Optimization ellapsed time:", t_end - t_start, "seconds")
print("Best value:", optimizer.fx_opt, "at [Tmax, Tmin]:", optimizer.x_opt)
optimizer.plot_acquisition(filename="/home/scom/pictures/bayesian_optimization/posterior_acquisition_iteration%.03i.png" % (n_iter+1))
optimizer.plot_convergence(filename="/home/scom/pictures/bayesian_optimization/posterior_convergence_iteration%.03i.png" % (0))
