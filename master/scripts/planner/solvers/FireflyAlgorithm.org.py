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

def compare_fireflyAlgorithm(iteration, **kwargs):
    bestFirefly1 = []
    for i in range(10):
        bestFirefly_tmp = fireflyAlgorithm(i, d=args.d, i=iteration, g=args.g, a=int(args.a), f=args.f, e=args.e, v=1, p=args.p, s=args.s, sch=args.sch)
        bestFirefly1.append(bestFirefly_tmp.luminosity)
    bestFirefly2 = []
    for i in range(10):
        bestFirefly_tmp = fireflyAlgorithm(i, d=args.d, i=iteration, g=args.g, a=int(args.a), f=args.f, e=args.e, v=4, p=args.p, s=args.s, sch=args.sch)
        bestFirefly2.append(bestFirefly_tmp.luminosity)
    average1 = sum(bestFirefly1)/len(bestFirefly1)
    average2 = sum(bestFirefly2)/len(bestFirefly2)
    return (bestFirefly1, bestFirefly2, average1, average2)

def displayPlot(tab,n):
    plt.plot(tab,tab[1])
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
                        c = betaStep(swarm[j].x, swarm[i].x, kwargs['g'])
                        #print(kwargs['v'])
                        if kwargs['v'] == 1:
                            c = alphaStep1(c, kwargs['a'])
                        elif kwargs['v'] == 2:
                            c = alphaStep2(c, kwargs['a'])
                        elif kwargs['v'] == 3:
                            c = alphaStep3(c, kwargs['a'])
                        elif kwargs['v'] == 4 :
                            c = alphaStep4(c, kwargs['a'], t, kwargs['s'], kwargs['sch'])
                        else :
                            c = alphaStep5(c, kwargs['a'], t, kwargs['s'], kwargs['sch'])
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
                    c = alphaStep4(c, kwargs['a'], t, kwargs['s'], kwargs['sch'])
                else :
                    c = alphaStep5(c, kwargs['a'], t, kwargs['s'], kwargs['sch'])
                swarm[i].update(c)
            swarm = sorted(swarm, key = lambda ff: ff.luminosity)
        if bestFirefly.luminosity > swarm[0].luminosity:
            bestFirefly = copy.deepcopy(swarm[0])
        if t % 100 == 0:
            if kwargs['p'] == 1:
                print("")
                print("Iteration: ", t)
                print("Swarm: ", [s.luminosity for s in swarm])
                print("Best firefly: ", bestFirefly.luminosity)
            tab[0].append(t+1)
            tab[1].append(bestFirefly.luminosity)
        t += 1
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
    parser.add_argument("-i", type = int, default = 10000, help = "number of iterations")
    parser.add_argument("-g", type = float, default = 0.90, help = "firefly algorithm gamma")
    parser.add_argument("-a", type = float, default = 1, help = "firefly algorithm alpha")
    parser.add_argument("-f", type = int, default = 10, help = "number of fireflies")
    parser.add_argument("-e", type = float, default = 0.1, help = "distance penalization coeficient")
    parser.add_argument("-v", type = int, default = 1, help = "alpha version")
    parser.add_argument("-n", type = int, default = 1, help = "number of runs")
    parser.add_argument("-p", type = int, default = 1, help = "enable/desable verbose")
    parser.add_argument("-s", type = int, default = 1, help = "step")
    parser.add_argument("-sch", type = str, default = "linear", help = "segment schedule")
    args = parser.parse_args()

    # if args.v == 1 or args.v == 2 or args.v == 4:
    #     args.a = int(args.a)
    if not os.path.exists("plots"):
        os.makedirs("plots")
    iterations = [10, 100, 1000, 10000, 100000, 1000000]
    for j in range(len(iterations)):
        with open("compare_algorithm_ite{}".format(iterations[j]), "w") as f:
            if args.p == 1:
                print("cleaning previous results")
        bestFirefly1, bestFirefly2, average1, average2 = compare_fireflyAlgorithm(iterations[j], d=args.d, i=iterations[j], g=args.g, a=args.a, f=args.f, e=args.e, v=args.v, p=args.p, s=args.s, sch=args.sch)
        with open("compare_algorithm_ite{}".format(iterations[j]), "a") as f:
            f.write("iteration : {}\n\n".format(iterations[j]))
            f.write("alphaStep1 (mean:{})\n".format(average1))
            for i in bestFirefly1:
                f.write("{}\n".format(i))
            f.write("\n")
            f.write("alphaStep4 (mean:{})\n".format(average2))
            for i in bestFirefly2:
                f.write("{}\n".format(i))
    # with open("compare_algorithm", "w") as f:
    #     if args.p == 1:
    #         print("cleaning previous results")
    # for i in range(args.n):
    #     bestFirefly = fireflyAlgorithm(i, d=args.d, i=args.i, g=args.g, a=args.a, f=args.f, e=args.e, v=args.v, p=args.p, s=args.s, sch=args.sch)
    #     if args.p == 1:
    #         print("Best firefly path: ", bestFirefly.x)
    #         print("Best firefly luminosity: ", bestFirefly.luminosity)
    #     with open("a5_linear_results_ite", "a") as f:
    #         f.write("{}\n".format(bestFirefly.luminosity))
