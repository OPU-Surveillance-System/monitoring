import argparse
import copy
import distance
import math
import os
import random
import time

def getEUC_Distance(a, b):#a, b: checkpoints
    d = math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
    d += 0.5
    return int(d)

def getPosition(title):
    with open(title, 'r') as f:
        lines = f.readlines()
    flag = False
    points = []
    for line in lines:
        if line.find('EOF') >= 0:
            break
        elif flag == True:
            tmp = line.strip().split()
            points.append((float(tmp[1]), float(tmp[2])))
        elif line.find('NODE_COORD_SECTION') >= 0:
            flag = True
    return points

# def getRoute():
#     with open("tsp/a280.opt.tour", "r") as f:
#         lines = f.readlines()
#     flag = False
#     route = []
#     for line in lines:
#         if line.find("-1") >= 0:
#             break
#         elif flag == True:
#             route.append(int(line.strip())-1)
#         elif line.find("TOUR_SECTION") >= 0:
#             flag = True
#
#     if route[-1] == -2:
#         route[-1] = -1
#     return route

class firefly:
    def __init__(self, points):
        self.route = [i for i in range(len(points))]
        random.shuffle(self.route)
        self.update(self.route, points)

    def update(self, route, points):
        self.luminosity = getRouteDistance(route, points)

    # def evaluate(self, route):
    #     return getRouteDistance(route)

def betaStep(a, b, gamma): #move a to b
    d = distance.hamming(a, b)
    beta = 1 / (1+gamma*d*d)
    new_route = ['' for i in a]
    to_insert = [i for i in a]
    # for i in range(len(a)):
    #     if a[i] == b[i]:
    #         new_route[i] = a[i]
    #         to_insert.remove(a[i])
    idx_rand=[i for i in range(len(a))]
    random.shuffle(idx_rand)
    visited_dic={i:'NOT_VISIT' for i in idx_rand}
    for idx in range(len(idx_rand)):
        if a[idx] == b[idx]:
            new_route[idx] = a[idx]
            visited_dic[a[idx]] = 'VISITED'
            to_insert.remove(a[idx])
            idx_rand.remove(idx)
    for idx in idx_rand:
        if beta < random.random():
            if visited_dic[a[idx]] == 'NOT_VISIT':
                new_route[idx] = a[idx]
                to_insert.remove(a[idx])
                visited_dic[a[idx]] = 'VISITED'
            elif visited_dic[b[idx]] == 'NOT_VISIT':
                new_route[idx] = b[idx]
                to_insert.remove(b[idx])
                visited_dic[b[idx]] = 'VISITED'
        else:
            if visited_dic[b[idx]] == 'NOT_VISIT':
                new_route[idx] = b[idx]
                to_insert.remove(b[idx])
                visited_dic[b[idx]] = 'VISITED'
            elif visited_dic[a[idx]] == 'NOT_VISIT':
                new_route[idx] = a[idx]
                to_insert.remove(a[idx])
                visited_dic[a[idx]] = 'VISITED'
    # for idx in random.sample(idx_rand, int(len(idx_rand)*beta)):
    #     new_route[idx] = b[idx]
    #     visited_dic[b[idx]] = 'VISITED'
    #     to_insert.remove(b[idx])
    #     idx_rand.remove(idx)
    # idx_rand_copy = [i for i in idx_rand]
    # for idx in idx_rand_copy:
    #     if visited_dic[a[idx]] == 'NOT_VISIT':
    #         new_route[idx] = a[idx]
    #         visited_dic[a[idx]] = 'VISITED'
    #         to_insert.remove(a[idx])
    #         idx_rand.remove(idx)
    #     elif visited_dic[b[idx]] == 'NOT_VISIT':
    #         new_route[idx] = b[idx]
    #         visited_dic[b[idx]] = 'VISITED'
    #         to_insert.remove(b[idx])
    #         idx_rand.remove(idx)

    # print('before insert{}'.format(new_route))
    random.shuffle(to_insert)
    while len(to_insert) > 0:
        idx = new_route.index('')
        new_route[idx] = to_insert.pop()

    return new_route

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

def fireflyAlgorithm(**kwargs):
    points = getPosition(kwargs['title'])
    swarm = [firefly(points) for i in range(kwargs['f'])]
    swarm = sorted(swarm, key = lambda ff: ff.luminosity)
    best_firefly = copy.deepcopy(swarm[0])
    # sorted_swarm = sorted(swarm, key = lambda ff: ff.luminosity)
    # best_firefly = copy.deepcopy(sorted_swarm[0])
    if kwargs['p']:
        print(kwargs)
        print('Best Firefly Luminosity: {}'.format(best_firefly.luminosity))
    iteration = 0
    start_time = time.time()

    # swarm[0].route=[0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,24,23,25,26,27,28,29,1]
    # swarm[0].update(swarm[0].route, points)

    while iteration < kwargs['i']:
        for i in range(kwargs['f']):
            for j in range(kwargs['f']):
                if i != j and swarm[i].luminosity < swarm[j].luminosity:
                    firefly_tmp = betaStep(swarm[j].route, swarm[i].route, kwargs['g'])
                    if kwargs['v'] == 5:
                        firefly_tmp = alphaStep5(firefly_tmp, kwargs['a'], iteration, kwargs['s'], kwargs['sch'])
                    swarm[j].update(firefly_tmp, points)
        swarm = sorted(swarm, key = lambda ff: ff.luminosity)
        if swarm[0].luminosity == swarm[-1].luminosity: #If all the fireflies are at the same point
            if kwargs['p'] == 1:
                print('***swarm blocked***')
            for i in range(1, kwargs['f']):
                if kwargs['v'] == 5:
                    swarm[i].route = alphaStep5(swarm[i].route, kwargs['a'], iteration, kwargs['s'], kwargs['sch'])
                swarm[i].update(swarm[i].route, points)
            swarm = sorted(swarm, key = lambda ff: ff.luminosity)
        if best_firefly.luminosity > swarm[0].luminosity:
            best_firefly = copy.deepcopy(swarm[0])
        if iteration % 50 == 0:
            if kwargs['p'] == 1:
                print('')
                print('Iteration: ', iteration)
                print('swarm: ', [s.luminosity for s in swarm])
                print('Best Firefly: ', best_firefly.luminosity)
            # with open('tsp/{}'.format(kwargs['name']), 'a') as f:
            #     f.write('{}\n'.format(best_firefly.luminosity))
        # print('==time1-2: ', time2-time1)
        # print('  time2-3: ', time3-time2)
        # print('  time3-4: ', time4-time3)
        iteration+=1

    end_time = time.time()
    if kwargs['p'] == 1:
        print('Elapsed Time: ', end_time - start_time)
    # with open('tsp/{}'.format(kwargs['name']), 'a') as f:
    #     f.write('Elapsed Time: {}\n'.format(end_time - start_time))

    return best_firefly



    # return betaStep(swarm[6].route, swarm[0].route, kwargs["g"])
    # return betaStep(a, b, kwargs["g"])
    # for i in swarm:
    #     print(i.luminosity)
    # return

def getRouteDistance(route, points):
    all_distance = 0
    for i in range(len(route)-1):
        all_distance += getEUC_Distance(points[route[i]], points[route[i+1]])
    all_distance += getEUC_Distance(points[route[-1]], points[route[0]])
    return all_distance

### When you cannot use arguments, activate these lines.
import easydict
args = easydict.EasyDict({
    'title' : 'tsp/oliver30.tsp',
    'name' : 'tsptest',
    'f' : 100,
    'a' : 10,
    'g' : 0.0005,
    'i' : 20000,
    'v' : 5,
    'p' : 1,
    's' : 20000000000,
    'sch' : 'linear'
})
###

if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-title", type = str, required = True, help = "tsp_Title")
    # parser.add_argument("-name", type= str, default = True, help="file name")
    # parser.add_argument("-a", type = int, default = 1, help = "alpha parameter")
    # parser.add_argument("-g", type = float, default = 0.90, help = "firefly algorithm gamma")
    #     # The smaller gamma, the more exploitation
    # parser.add_argument("-i", type = int, default = 100, help = "iteration")
    # parser.add_argument("-v", type = int, default = 5, help = "alpha version")
    # parser.add_argument("-p", type = int, default = 1, help = "enable/desable verbose")
    # parser.add_argument("-f", type = int, default = 10, help = "the number of fireflies")
    # parser.add_argument("-s", type = int, default = 1, help = "step")
    #     # The larger step, the faster the segment decreases
    # parser.add_argument("-sch", type = str, default = 'linear', help = "schedule linear/sqrt")
    # args = parser.parse_args()

    if not os.path.exists('tsp/{}'.format(args.name)):
        with open('tsp/{}'.format(args.name), 'w') as f:
            print('clean previous result')
    best_firefly = fireflyAlgorithm(title=args.title, name=args.name, a=args.a, g=args.g, i=args.i, v=args.v, p=args.p, f=args.f, s=args.s, sch=args.sch)
    # with open('tsp/{}'.format(args.name), 'a') as f:
    #     f.write('best_firefly: {}\n\n'.format(best_firefly.luminosity))
    # all_distance = getRouteDistance(route)
    # print(points)
    # print(route)

    # a = [4, 7, 9, 1, 3, 2, 5, 6, 8]
    # b = [4, 3, 8, 9, 7, 2, 5, 6, 1]
    #
    # print(betaStep(a, b, args.g))

    # print(best_firefly)
