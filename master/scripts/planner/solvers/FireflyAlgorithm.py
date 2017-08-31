import random
import math
import distance
import copy
import argparse
import time
import os

import matplotlib.pyplot as plt

from sys import path

path.append("..")

path.append("../..")

import pickle
with open("../../webserver/data/serialization/mapper.pickle", "rb") as f:
        mapper = pickle.load(f)

#open("H:\Documents\JaponStageLabo\mapper.pickle", "rb")
#open("../../webserver/data/serialization/mapper.pickle", "rb")

import settings

points = [(32, 1122), (271, 1067), (209, 993), (184, 1205), (303, 1220), (400, 1122), (505, 1214), (669, 1202), (779, 1026), (912, 1029), (1483, 1156), (1614, 991), (1576, 567), (1502, 395), (1618, 227), (1448, 634), (967, 690), (1059, 842), (759, 823), (1387, 174), (1073, 82), (944, 327), (866, 512), (748, 638), (487, 896), (118, 653), (35, 902), (502, 339), (683, 316), (694, 123), (45, 52), (367, 39)]

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d", type = int, default = 2, help = "number of drones")
parser.add_argument("-i", type = int, default = 10000, help = "number of iterations")
parser.add_argument("-g", type = float, default = 0.1, help = "firefly algorithm gamma")
parser.add_argument("-a", type = float, default = 2, help = "firefly algorithm alpha")
parser.add_argument("-f", type = int, default = 10, help = "number of fireflies")
parser.add_argument("-e", type = float, default = 0.1, help = "distance penalization coeficient")
parser.add_argument("-v", type = int, default = 1, help = "alpha version")
parser.add_argument("-n", type = int, default = 1, help = "number of runs")
args = parser.parse_args()
if args.v == 1 or args.v == 2:
    args.a = int(args.a)

# Firefly class
class firefly:
    def __init__(self,  p):
        self.eta = args.e
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
        last_position = [mapper.starting_point[i] for i in range(args.d)]
        start = [p for p in last_position]
        point_time = {}
        drone_elapsed_time = [0 for i in range(args.d)]
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
                if d >= args.d:
                    d = 0
        for d in range(args.d):
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
def betaStep(a, b):
    a2 = [element for subList in a for element in subList]
    b2 = [element for subList in b for element in subList]
    d = distance.hamming(a2, b2)
    beta = 1 / (1 + args.g * d)
    c = ['' for i in a2]
    toInsert = [i for i in a2]
    for i in range(len(a2)):
        if a2[i] == b2[i] or random.random() < args.g:
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
def alphaStep1(a):
    for i in range(args.a):
        x = random.randint(0, len(a)-1)
        y = random.randint(0, len(a)-1)
        a[x], a[y] = a[y], a[x]
    return a

# Alpha step: exploration (v2)
def alphaStep2(a):
    idxs = [i for i in range(len(a))]
    random.shuffle(idxs)
    x = idxs[0:args.a]
    y = idxs[0:args.a]
    random.shuffle(y)
    for i in range(args.a):
        a[x[i]],  a[y[i]] = a[y[i]], a[x[i]]
    return a

# Alpha step: exploration (v3)
def alphaStep3(a):
    a2 = [element for element in a]
    random.shuffle(a2)
    b2 = [element for element in a]
    c = ['' for i in a2]
    toInsert = [i for i in a2]
    for i in range(len(a2)):
        if a2[i] == b2[i] or random.random() < args.a:
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

def displayPlot(tab,n):
    plt.plot(tab[0],tab[1])
    plt.xlabel('Iteration')
    plt.ylabel('Best Firefly Luminosity')
    plt.savefig("plots/%d.svg"%(n), format="svg")
    #plt.show()
    plt.clf()

# Firefly algorithm
def fireflyAlgorithm(z):
    swarm = [firefly(points) for i in range(args.f)]
    swarm = sorted(swarm, key = lambda ff: ff.luminosity)
    bestFirefly = copy.deepcopy(swarm[0])
    print("Best firefly init: ", bestFirefly.luminosity)
    tab = ([0], [bestFirefly.luminosity])
    t = 0
    n = len(swarm)
    startTime = time.time()
    while t < args.i:
        for i in range(n):
            for j in range(n):
                if j != i:
                    if swarm[j].luminosity < swarm[i].luminosity:
                        c = betaStep(swarm[j].x,swarm[i].x)
                        if args.v == 1:
                            c = alphaStep1(c)
                        elif args.v == 2:
                            c = alphaStep2(c)
                        else:
                            c = alphaStep3(c)
                        swarm[i].update(c)
        swarm = sorted(swarm, key = lambda ff: ff.luminosity)
        if bestFirefly.luminosity > swarm[0].luminosity:
            bestFirefly = copy.deepcopy(swarm[0])
        if t % 100 == 0:
            print("")
            print("Iteration: ", t)
            print("Swarm: ", [s.luminosity for s in swarm])
            print("Best firefly: ", bestFirefly.luminosity)
            tab[0].append(t+1)
            tab[1].append(bestFirefly.luminosity)
        t += 1
    endTime = time.time()
    print("Elapsed time: ", endTime - startTime)
    displayPlot(tab,z)
    return bestFirefly

if __name__ == "__main__":
    if not os.path.exists("plots"):
        os.makedirs("plots")
    with open("results", "w") as f:
        print("cleaning previous results")
    for i in range(args.n):
        bestFirefly = fireflyAlgorithm(i)
        print("Best firefly path: ", bestFirefly.x)
        print("Best firefly luminosity: ", bestFirefly.luminosity)
        with open("results", "a") as f:
            f.write("{}\n".format(bestFirefly.luminosity))
