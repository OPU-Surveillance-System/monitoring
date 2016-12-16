import GPy
import GPyOpt
import numpy as np
from sys import path
import pickle
import time
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
    mean = []
    for i in range(20):
        rplan = RandomSolver(state, mapper, nb_drone)
        rplan.solve()
        saplan = SimulatedAnnealingSolver(rplan.state, mapper, nb_drone)
        saplan.copy_strategy = "slice"
        saplan.steps = 2000000
        saplan.Tmax = x[:,0]
        saplan.Tmin = x[:,1]
        saplan.updates = 0
        itinerary, energy = saplan.solve()
        mean.append(energy)
    mean = sum(mean) / len(mean)
    mean = np.array(energy)
    print("x:", x[:,0], x[:,1], "f:", mean)

    return mean.reshape(1, 1)

print("Initialization")
bounds =[{'name': 'tmax', 'type': 'continuous', 'domain': (0.01, 10000)},
         {'name': 'tmin', 'type': 'continuous', 'domain': (0.01, 10000)}]
constrains = [{'name': 'constraint', 'constrain': 'x[:,1] - x[:,0]'}]
optimizer = GPyOpt.methods.BayesianOptimization(bayesian_optimization_min_dist_simulated_annealing,
                                                domain = bounds,
                                                constrains = constrains,
                                                model_type = 'GP',
                                                acquisition_type = 'EI',
                                                initial_design_numdata=10,
                                                model_update_interval=1,
                                                normalize_Y = True,
                                                evaluator_type='sequential',
                                                batch_size=1,
                                                num_cores=1,
                                                acquisition_jitter=0)
optimizer.plot_acquisition(filename="/home/scom/pictures/bayesian_optimization/iteration%.03i.png" % (0))
n_iter = 100
t_start = time.time()
print("Start optimization")
# for i in range(n_iter):
#     print("Iteration:", i)
# optimizer.run_optimization(max_iter=1, verbosity = True)
# optimizer.plot_acquisition(filename="/home/scom/pictures/bayesian_optimization/iteration%.03i.png" % (i + 1))
optimizer.run_optimization(max_iter=n_iter, eps=-1.0, verbosity = True)
t_end = time.time()
print("Ellapsed time:", t_end - t_start, "seconds")
print("Best value:", optimizer.fx_opt, "at [Tmax, Tmin]:", optimizer.x_opt)
optimizer.plot_acquisition()
optimizer.plot_convergence()
