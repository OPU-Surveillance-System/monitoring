import random
import math
import distance
import copy
import argparse
import time
import os
import matplotlib.pyplot as plt
from sys import path
import pickle
import scipy
import scipy.stats
import scipy.optimize
import numpy as np

import lehmer

path.append("..")

path.append("../..")
import settings

with open("../../webserver/data/serialization/mapper.pickle", "rb") as f:
        mapper = pickle.load(f)

# Firefly class
class firefly:
    def __init__(self, p, eta, nb_drone):
        self.eta = eta
        self.nb_drone = nb_drone
        points = [element for element in p]
        random.shuffle(points)
        self.update(points)

    # Update fireflies data
    def update(self, x):
        uncertainty, distance, solution = self.evaluate(x)
        self.x = solution
        self.uncertainty = uncertainty
        self.distance = distance
        self.luminosity = 10000 * uncertainty + self.eta * distance

    # Build the paths from a list of points
    def evaluate(self, x):
        checkpoints = [element for element in x]
        limit = 0
        battery = 0
        last_position = [mapper.starting_point[i] for i in range(self.nb_drone)]
        start = [p for p in last_position]
        point_time = {}
        drone_elapsed_time = [0 for i in range(self.nb_drone)]
        d = 0
        solution = []
        way = []
        while len(checkpoints) > 0:
            if limit + mapper.paths[(last_position[d], checkpoints[0])][1] + mapper.paths[(checkpoints[0], start[d])][1] < 3000:
                path = mapper.paths[(last_position[d], checkpoints[0])][1]
                limit += path
                drone_elapsed_time[d] += path * 0.5
                point_time[checkpoints[0]] = drone_elapsed_time[d]
                way.append(checkpoints[0])
                last_position[d] = checkpoints.pop(0)
            else:
                solution.append(way)
                way = []
                path = mapper.paths[(last_position[d], start[d])][1]
                battery += limit + path
                limit = 0
                drone_elapsed_time[d] += path * 0.5
                last_position[d] = start[d]
                d += 1
                if d >= self.nb_drone:
                    d = 0
        for d in range(self.nb_drone):
            if last_position[d] != start[d]:
                solution.append(way)
                path = mapper.paths[(last_position[d], start[d])][1]
                battery += limit + path
                drone_elapsed_time[d] += path * 0.5
        end_patrol_time = max(drone_elapsed_time)
        mean = []
        for element in list(point_time.values()):
            mean.append(1 - math.exp(-0.001279214 * (end_patrol_time - element)))
        mean = sum(mean) / len(mean)
        return mean, battery, solution

class binomial():
    def __init__(self, a, b, confidence_mass):
        """
        hdi constructor:
            a, b: Initial Beta distribution parameters (float > 0)
            confidence_mass: Highest Density Interval (HDI)'s span (float 0 < x < 1)
        """
        self.a = a
        self.b = b
        self.confidence_mass = confidence_mass
        self.distrib = scipy.stats.beta(a, b)
        self.hdi = self.get_hdi()

    def get_hdi(self):
        """
        Compute the Highest Density Interval of the team's distribution:
        Adapted from: https://stackoverflow.com/questions/22284502/highest-posterior-density-region-and-central-credible-region
        """
        inconfidence_mass = 1 - self.confidence_mass

        def get_interval_width(low_tail):
            interval_width = self.distrib.ppf(self.confidence_mass + low_tail) - self.distrib.ppf(low_tail)

            return interval_width

        hdi_low_tail = scipy.optimize.fmin(get_interval_width, inconfidence_mass, ftol=1e-8, disp=False)[0]
        hdi = self.distrib.ppf([hdi_low_tail, self.confidence_mass + hdi_low_tail])

        return hdi

    def update(self, n, z):
        """
        Update the Beta distribution:
            n: number of fireflyAlgorithm runs
            z: number of alpha5 > alpha2 (alpha5 is better than alpha2)
        """
        self.a += z
        self.b += n - z
        self.distrib = scipy.stats.beta(self.a, self.b)
        self.hdi = self.get_hdi()

# Beta step: exploitation
def betaStep(a, b, gamma):
    a2 = [element for subList in a for element in subList]
    b2 = [element for subList in b for element in subList]
    d = distance.hamming(a2, b2)
    beta = 1 / (1 + gamma * d)
    c = ['' for i in a2]
    toInsert = [i for i in a2]
    for i in range(len(a2)):
        if a2[i] == b2[i] or random.random() < beta:
            if a2[i] not in c:
                c[i] = a2[i]
                toInsert.remove(a2[i])
        else:
            if b2[i] not in c:
                c[i] = b2[i]
                toInsert.remove(b2[i])
    while len(toInsert) > 0:
        idx = c.index('')
        c[idx] = toInsert.pop()
    return c

# Alpha step: exploration (v1)
def alphaStep1(a, alpha):
    for i in range(alpha):
        x = random.randint(0, len(a)-1)
        y = random.randint(0, len(a)-1)
        a[x], a[y] = a[y], a[x]
    return a

# Alpha step: exploration (v2)
def alphaStep2(a, alpha):
    idxs = [i for i in range(len(a))]
    random.shuffle(idxs)
    x = idxs[0:alpha]
    y = idxs[0:alpha]
    random.shuffle(y)
    for i in range(alpha):
        a[x[i]],  a[y[i]] = a[y[i]], a[x[i]]
    return a

# Alpha step: exploration (v3)
def alphaStep3(a, alpha):
    a2 = [element for element in a]
    random.shuffle(a2)
    b2 = [element for element in a]
    c = ['' for i in a2]
    toInsert = [i for i in a2]
    for i in range(len(a2)):
        if a2[i] == b2[i] or random.random() < alpha:
            if a2[i] not in c:
                c[i] = a2[i]
                toInsert.remove(a2[i])
        else:
            if b2[i] not in c:
                c[i] = b2[i]
                toInsert.remove(b2[i])
    while len(toInsert) > 0:
        idx = c.index('')
        c[idx] = toInsert.pop()
    return c

# Alpha step: exploration (v4)
def alphaStep4(a, alpha, t, step, schedule):
    if schedule == "linear":
        segment = len(a) - (t//step)
    elif schedule == "sqrt":
        segment = int(len(a) - (t//step)**(1/2))
    if segment < 2:
        segment = 2
    origin = random.randint(0, len(a)-1)
    end = origin + segment
    for i in range(alpha):
        x = random.randint(origin, end) % len(a)
        y = random.randint(origin, end) % len(a)
        a[x], a[y] = a[y], a[x]
    return a

# Alpha step: exploration (v5)
def alphaStep5(a, alpha, t, step, schedule):
    if schedule == "linear":
        segment = len(a) - (t//step)
    elif schedule == "sqrt":
        segment = int(len(a) - (t//step)**(1/2))
    if segment < 2:
        segment = 2
    if alpha > segment:
        alpha = segment
    origin = random.randint(0, len(a)-1)
    end = origin + segment
    idxs = [i for i in range(origin, end)]
    for i in range(len(idxs)):
        idxs[i] = idxs[i]%len(a)
    random.shuffle(idxs)
    alpha = int(alpha)
    x = idxs[0:alpha]
    y = idxs[0:alpha]
    random.shuffle(y)
    for i in range(alpha):
        a[x[i]],  a[y[i]] = a[y[i]], a[x[i]]
    return a

# Alpha step: exploration (v6)
# Generate random alpha parameter according with a normal or exponential distribution
def alphaStep6(a, delta):
    alpha = math.ceil(np.random.exponential(delta, 1)*32)
    if alpha > len(a):
        alpha = len(a)
    elif alpha < 2:
        alpha = 2
    idxs = [i for i in range(len(a))]
    random.shuffle(idxs)
    x = idxs[0:alpha]
    y = idxs[0:alpha]
    random.shuffle(y)
    for i in range(alpha):
        a[x[i]],  a[y[i]] = a[y[i]], a[x[i]]
    return a

def compare_fireflyAlgorithm(iteration, **kwargs):
    bestFireflies1 = []
    for i in range(10):
        bestFirefly_tmp = fireflyAlgorithm(i, d=args.d, i=iteration, g=0.01502, a=8, f=93, e=args.e, v=2, p=args.p, s=args.s, sch=args.sch)
        bestFireflies1.append(bestFirefly_tmp.luminosity)
    bestFireflies2 = []
    for i in range(10):
        bestFirefly_tmp = fireflyAlgorithm(i, d=args.d, i=iteration, g=0.0039, a=30, f=89, e=args.e, v=5, p=args.p, s=24, sch=args.sch)
        bestFireflies2.append(bestFirefly_tmp.luminosity)
    average1 = sum(bestFireflies1)/len(bestFireflies1)
    average2 = sum(bestFireflies2)/len(bestFireflies2)
    better_ff2 = 0
    for bestFirefly1, bestFirefly2 in zip(bestFireflies1, bestFireflies2):
        if bestFirefly1 > bestFirefly2: #小さいほうが良い
            better_ff2+=1
    return (bestFireflies1, bestFireflies2, average1, average2, better_ff2)

def displayPlot(tab,n):
    plt.plot(tab[0],tab[1])
    plt.xlabel('Iteration')
    plt.ylabel('Best Firefly Luminosity')
    plt.savefig("plots/%d.svg"%(n), format="svg")
    plt.clf()

def plotConvergence(lehmer_hist):
    for l in range(len(lehmer_hist)):
        x = [l for i in range(len(lehmer_hist[l]))]
        plt.scatter(x[1:], lehmer_hist[l][1:], c='g')
        plt.scatter(x[0], lehmer_hist[l][0], c='r')
    plt.xlabel('Firefly algorithm\'s generation')
    plt.ylabel('Lehmer code')
    plt.savefig("plots/convergence.svg", format="svg")
    plt.clf()(1/(math.sqrt(t)+1))//step

def displaySegment(segment):
    x = list(range(len(segment)))
    plt.plot(x, segment)
    plt.xlabel('')
    plt.ylabel('Segment size')
    plt.savefig("plots/segment.svg", format="svg")
    plt.clf()

def displayBeta(a, b, iteration):#a, b: Beta distribution parameters
    x = np.linspace(0, 1, 100)
    plt.xlim(0, 1)
    plt.ylim(0, 5)
    # label
    rv = scipy.stats.beta(a, b)
    y = rv.pdf(x)
    plt.plot(x, y)
    plt.savefig("hdi/iteration{}/beta_distrib_ite{}.svg".format(iteration, iteration), format="svg")
    plt.clf()

# Firefly algorithm
def fireflyAlgorithm(z, **kwargs):
    if kwargs['p']:
        print(kwargs)
    points = [(32, 1122), (271, 1067), (209, 993), (184, 1205), (303, 1220), (400, 1122), (505, 1214), (669, 1202), (779, 1026), (912, 1029), (1483, 1156), (1614, 991), (1576, 567), (1502, 395), (1618, 227), (1448, 634), (967, 690), (1059, 842), (759, 823), (1387, 174), (1073, 82), (944, 327), (866, 512), (748, 638), (487, 896), (118, 653), (35, 902), (502, 339), (683, 316), (694, 123), (45, 52), (367, 39)]
    swarm = [firefly(points, kwargs['e'], kwargs['d']) for i in range(kwargs['f'])]
    swarm = sorted(swarm, key = lambda ff: ff.luminosity)
    bestFirefly = copy.deepcopy(swarm[0])
    if kwargs['p'] == 1:
        print("Best firefly init: ", bestFirefly.luminosity)
    tab = ([0], [bestFirefly.luminosity])
    t = 0
    n = len(swarm)
    segment = []
    startTime = time.time()
    while t < kwargs['i']:
        for i in range(n):
            for j in range(n):
                if j != i:
                    if swarm[j].luminosity < swarm[i].luminosity:
                        time1 = time.time()
                        c = betaStep(swarm[j].x, swarm[i].x, kwargs['g'])
                        time2 = time.time()
                        #print(kwargs['v'])
                        if kwargs['v'] == 1:
                            c = alphaStep1(c, kwargs['a'])
                        elif kwargs['v'] == 2:
                            c = alphaStep2(c, kwargs['a'])
                        elif kwargs['v'] == 3:
                            c = alphaStep3(c, kwargs['a'])
                        elif kwargs['v'] == 4:
                            c = alphaStep4(c, kwargs['a'], t, kwargs['s'], kwargs['sch'])
                        elif kwargs['v'] == 5:
                            c = alphaStep5(c, kwargs['a'], t, kwargs['s'], kwargs['sch'])
                        else:
                            c = alphaStep6(c, kwargs['dl'])
                        swarm[i].update(c)
        swarm = sorted(swarm, key = lambda ff: ff.luminosity)
        if swarm[0].luminosity == swarm[-1].luminosity: #If all the fireflies are at the same position
            if kwargs['p'] == 1:
                print("*** swarm blocked ***")
            for i in range(1, len(swarm)):
                c = [element for subList in swarm[i].x for element in subList]
                if kwargs['v'] == 1:
                    c = alphaStep1(c, kwargs['a'])
                elif kwargs['v'] == 2:
                    c = alphaStep2(c, kwargs['a'])
                elif kwargs['v'] == 3:
                    c = alphaStep3(c, kwargs['a'])
                elif kwargs['v'] == 4:
                    if kwargs['c'] == 1:
                        c = alphaStep6(c, kwargs['dl'])
                    else:
                        c = alphaStep4(c, kwargs['a'], t, kwargs['s'], kwargs['sch'])
                elif kwargs['v'] == 5:
                    c = alphaStep5(c, kwargs['a'], t, kwargs['s'], kwargs['sch'])
                else:
                    c = alphaStep6(c, kwargs['dl'])
                swarm[i].update(c)
            swarm = sorted(swarm, key = lambda ff: ff.luminosity)
        time3 = time.time()
        if bestFirefly.luminosity > swarm[0].luminosity:
            bestFirefly = copy.deepcopy(swarm[0])
        time4 = time.time()
        if t % 100 == 0:
            if kwargs['p'] == 1:
                print("")
                print("Iteration: ", t)
                print("Swarm: ", [s.luminosity for s in swarm])
                print("Best firefly: ", bestFirefly.luminosity)
            tab[0].append(t+1)
            tab[1].append(bestFirefly.luminosity)
        t += 1
        with open("tsp/drone.time", "a") as f:
            f.write('--time1-2: {} '.format(time2-time1))
            f.write('--time2-3: {} '.format(time3-time2))
            f.write('--time3-4: {}\n\n'.format(time4-time3))
    endTime = time.time()
    if kwargs['p'] == 1:
        print("Elapsed time: ", endTime - startTime)
        #displayPlot(tab,z)
        #displaySegment(segment)
    return bestFirefly

if __name__ == "__main__":
    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", type = int, default = 2, help = "number of drones")
    parser.add_argument("-dl", type = float, default = 0.15, help = "firefly algorithm delta")
    parser.add_argument("-i", type = int, default = 10000, help = "number of iterations")
    parser.add_argument("-g", type = float, default = 0.90, help = "firefly algorithm gamma")
    parser.add_argument("-a", type = float, default = 1, help = "firefly algorithm alpha")
    parser.add_argument("-f", type = int, default = 10, help = "number of fireflies")
    parser.add_argument("-e", type = float, default = 0.1, help = "distance penalization coeficient")
    parser.add_argument("-v", type = int, default = 1, help = "alpha version")
    parser.add_argument("-c", type = int, default = 0, help = "change/not_change alphaStep4 to 6 when swarm block")
    parser.add_argument("-n", type = int, default = 1, help = "number of runs")
    parser.add_argument("-p", type = int, default = 1, help = "enable/desable verbose")
    parser.add_argument("-s", type = int, default = 1, help = "step")
    parser.add_argument("-sch", type = str, default = "linear", help = "segment schedule")
    args = parser.parse_args()
    # コマンドラインほぼ意味なし状態

    if args.v == 1 or args.v == 2 or args.v == 4 or args.v == 5:
        args.a = int(args.a)
    if not os.path.exists("plots"):
        os.makedirs("plots")
    bestFirefly = fireflyAlgorithm(0, d=args.d, dl=args.dl, i=args.i, g=args.g, a=args.a, f=args.f, e=args.e, v=args.v, c=args.c, p=args.p, s=args.s, sch=args.sch)
    # if not os.path.exists("hdi"):
    #     os.makedirs("hdi")
    # with open("hdi/hdi_results", "w") as f:
    #     if args.p == 1:
    #         print("cleaning previous hdi_results")
    # iterations = [100, 1000, 10000, 100000, 1000000]
    # for i in iterations:
    #     compare_algorithm_binomial = binomial(2, 2, 0.95)
    #     try_count = 0
    #     while compare_algorithm_binomial.hdi[0] < 0.5 and 0.5 < compare_algorithm_binomial.hdi[1]:
    #         if try_count < 100:
    #             with open("hdi/iteration{}/try{}".format(i, try_count), "w") as f:
    #                 if args.p == 1:
    #                     print("cleaning previous results")
    #             bestFireflies1, bestFireflies2, average1, average2, better_ff2 = compare_fireflyAlgorithm(i, d=args.d, dl=args.dl i=args.i, g=args.g, a=args.a, f=args.f, e=args.e, v=args.v, c=args.c, p=args.p, s=args.s, sch=args.sch)
    #             compare_algorithm_binomial.update(10, better_ff2)
    #             with open("hdi/iteration{}/try{}".format(i, try_count), "a") as f:
    #                 f.write("iteration : {}\ntry : {}\n\n".format(i, try_count))
    #                 f.write("alphaStep2 (mean:{})\n".format(average1))
    #                 for bestFirefly1 in bestFireflies1:
    #                     f.write("{}\n".format(bestFirefly1))
    #                 f.write("\n")
    #                 f.write("alphaStep5 (mean:{})\n".format(average2))
    #                 for bestFirefly2 in bestFireflies2:
    #                     f.write("{}\n".format(bestFirefly2))
    #                 f.write("\n")
    #                 f.write("alphaStep2 < alphaStep5 = {}".format(better_ff2))
    #             try_count += 1
    #         else :
    #             with open("hdi/hdi_results", "a") as f:
    #                     f.write("iteration{} : alphastep2 = alphastep5\n".format(i))
    #             break
    #     if compare_algorithm_binomial.hdi[0] > 0.5:
    #         with open("hdi/hdi_results", "a") as f:
    #                 f.write("iteration{} : alphastep2 < alphastep5\n".format(i))
    #     elif compare_algorithm_binomial.hdi[1] < 0.5:
    #         with open("hdi/hdi_results", "a") as f:
    #             f.write("iteration{} : alphastep2 > alphastep5\n".format(i))
    #     displayBeta(compare_algorithm_binomial.a, compare_algorithm_binomial.b, i)
    # with open("compare_algorithm", "w") as f:
    #     if args.p == 1:
    #         print("cleaning previous results")
    # for i in range(args.n):
        # bestFirefly = fireflyAlgorithm(i, d=args.d, i=args.i, g=args.g, a=args.a, f=args.f, e=args.e, v=args.v, p=args.p, s=args.s, sch=args.sch)
    #     if args.p == 1:
    #         print("Best firefly path: ", bestFirefly.x)
    #         print("Best firefly luminosity: ", bestFirefly.luminosity)
    #     with open("a5_linear_results_ite", "a") as f:
    #         f.write("{}\n".format(bestFirefly.luminosity))
