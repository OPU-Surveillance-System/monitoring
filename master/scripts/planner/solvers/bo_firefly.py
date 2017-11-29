import GPy
import GPyOpt
import argparse
import os
import numpy as np
import time

import FireflyAlgorithm as ffa

def func(var):
    hist = []
    gamma = var[:,0][0]
    alpha = var[:,1][0]
    fireflies = int(var[:,2][0] * 100)
    step = int(var[:,3][0] * 100)
    if args.v == 1 or args.v == 4:
        alpha = int(alpha * 16)
    if args.v == 2 or args.v == 5:
        alpha = int(alpha * 32)
    for i in range(args.n):
        best_firefly = ffa.fireflyAlgorithm(0, d=args.d, i=args.i, g=gamma, a=alpha, f=fireflies, e=args.e, v=args.v, p=args.p, s=step, sch=args.sch)
        hist.append(best_firefly.luminosity)
    res = np.array(hist).mean()
    print('Tried [Gamma, Alpha, #Fireflies, step] = [{}, {}, {}, {}], got {}'.format(gamma, alpha, fireflies, step, res))
    with open('bayesopt', 'a') as f:
        f.write('{}\t{}\t{}\t{}\t{}\n'.format(gamma, alpha, fireflies, step, res))

    return res

def main(args):
    with open('bayesopt', 'w') as f:
        print('cleaning previous results')
    # bounds = [{'name': 'gamma', 'type': 'continuous', 'domain': (0, 1)},
    #           {'name': 'alpha', 'type': 'continuous', 'domain': (0, 1)},
    #           {'name': 'nbfireflies', 'type': 'continuous', 'domain': (0.02, 1)}]
    bounds = [{'name': 'gamma', 'type': 'continuous', 'domain': (0.001, 1)},
              {'name': 'alpha', 'type': 'continuous', 'domain': (0, 1)},
              {'name': 'nbfireflies', 'type': 'continuous', 'domain': (0.02, 1)},
              {'name': 'step', 'type': 'continuous', 'domain': (0.01, 1)}]
    myBopt = GPyOpt.methods.BayesianOptimization(f = func,
                                                 domain = bounds,
                                                 model_type = 'GP',
                                                 acquisition_type = 'EI',
                                                 normalize_Y = True,
                                                 exact_feval = False,
                                                 initial_design_numdata = 8,
                                                 evaluator_type = 'local_penalization',
                                                 batch_size = 4,
                                                 num_cores = 4)
    max_iter = args.m
    t_start = time.time()
    myBopt.run_optimization(max_iter)
    best_value = myBopt.fx_opt[0]
    best_gamma = myBopt.x_opt[0]
    best_alpha = myBopt.x_opt[1]
    if args.v == 1 or args.v == 4:
        best_alpha = int(best_alpha * 16)
    if args.v == 2 or args.v == 5:
        best_alpha = int(best_alpha * 32)
    best_fireflies = int(myBopt.x_opt[2] * 100)
    best_step = int(myBopt.x_opt[3] * 100)
    print('Best value: {} at [Gamma, Alpha, #Firefly, step] = [{}, {}, {}, {}], found in {} s'.format(best_value, best_gamma, best_alpha, best_fireflies, best_step, time.time() - t_start))
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", type = int, default = 100, help = "number of max iterations")
    parser.add_argument("-d", type = int, default = 2, help = "number of drones")
    parser.add_argument("-i", type = int, default = 10000, help = "number of iterations")
    parser.add_argument("-e", type = float, default = 0.1, help = "distance penalization coeficient")
    parser.add_argument("-v", type = int, default = 1, help = "alpha version")
    parser.add_argument("-n", type = int, default = 1, help = "number of runs")
    parser.add_argument("-p", type = int, default = 1, help = "enable/desable verbose")
    parser.add_argument("-s", type = int, default = 1, help = "step")
    parser.add_argument("-sch", type = str, default = "linear", help = "segment schedule")
    args = parser.parse_args()
    main(args)
