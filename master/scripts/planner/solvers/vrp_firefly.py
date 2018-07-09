import argparse
import copy
import distance
import math
import numpy as np
import sys
import os
import time
import xml.etree.ElementTree as ET

def confirm_input(fname):
    while True:
        choice = input("delete previous '{}' ?[y/n]: ".format(fname)).lower()
        if choice == 'y':
            return True
        elif choice == 'n':
            sys.exit()

def calc_EUCdistance(a, b):#a, b: customers
    d = math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
    return d

def extract_xmldata(bmark):
    tree = ET.parse('{}'.format(bmark))
    root = tree.getroot()

    coordx = []
    coordy = []
    for x in root.iter('CoordX'):
        x = int(x.text)
        coordx.append(x)
    for y in root.iter('CoordY'):
        y = int(y.text)
        coordy.append(y)
    coord = [(x,y) for x,y in zip(coordx, coordy)]

    forbidden_i = []
    forbidden_j = []
    #forbidden_i to forbidden_j
    for i in root.iter('est1'):
        i = int(i.text)
        forbidden_i.append(i)
    for j in root.iter('est2'):
        j = int(j.text)
        forbidden_j.append(j)
    forbidden = [(i, j) for i, j in zip(forbidden_i, forbidden_j)]

    cluster = set()
    for i in root.iter('Cluster'):
        i = int(i.text)
        cluster.add(i)

    dem_ent = []
    dem_rec = []
    for i in root.iter('DemEnt'):
        i = int(i.text)
        dem_ent.append(i)
    for j in root.iter('DemRec'):
        j = int(j.text)
        dem_rec.append(j)
    demand = [dem_ent[i] + dem_rec[i] for i in range(len(dem_ent))]

    return coord, forbidden, cluster, demand


class Firefly:
    def __init__(self, tour):
        self.VEHICLE_CAPACITY = 240 #Osaba_50_1_1
        ###TIME (second)[start, end]
        self.DELIVERY_TIME = [6*60*60, 15*60*60]
        self.PEAK_TIME = [8*60*60, 10*60*60]
        ###
        init_tour = copy.deepcopy(tour)
        tour2routes = [i for i in range(len(tour))]
        np.random.shuffle(tour2routes)
        for i in range(len(tour)):
            np.random.shuffle(init_tour[i])
        self.update(init_tour, tour2routes)
    def update(self, tour, tour2routes):
        routes, luminosity = self.evaluate(tour, tour2routes)
        self.tour = tour
        self.tour2routes = tour2routes
        self.routes = routes
        self.luminosity = luminosity
    def evaluate(self, tour, tour2routes):
        """
        tour: the permutation of customers in clusters
        and
        routes: the permutation of customers separated by zero
        If routes is coming, this function converts tour into routes.
        """
        global off_peak, peak, clustered_demand
        routes = []
        load_amount = 0
        routes.append(0)
        for cluster in tour2routes:
            if self.VEHICLE_CAPACITY < load_amount+clustered_demand[cluster+1]:
                routes.append(0)
                for customer in tour[cluster]:
                    routes.append(customer)
                load_amount = clustered_demand[cluster+1]
            else:
                for customer in tour[cluster]:
                    routes.append(customer)
                load_amount += clustered_demand[cluster+1]
        routes.append(0)

        # for i, demand in enumerate(clustered_demand):
        #     if self.VEHICLE_CAPACITY < load_amount+demand:
        #         routes.append(0)
        #         for customer in tour[i-1]:
        #             routes.append(customer)
        #         load_amount = demand
        #     else:
        #         if i == 0:
        #             routes.append(0)
        #         else:
        #             for customer in tour[i-1]:
        #                 routes.append(customer)
        #             load_amount += demand
        # routes.append(0)

        luminosity = 0
        triptime = self.DELIVERY_TIME[0]
        for i in range(len(routes)-1):
            if routes[i] == 0:
                if triptime != np.inf and self.DELIVERY_TIME[1] < triptime:
                    luminosity = 200000
                luminosity += triptime - self.DELIVERY_TIME[0]
                triptime = self.DELIVERY_TIME[0]
            if self.PEAK_TIME[0] <= triptime and triptime <= self.PEAK_TIME[1]:
                triptime += peak[routes[i]][routes[i+1]]
            else:
                triptime += off_peak[routes[i]][routes[i+1]]
        luminosity += triptime - self.DELIVERY_TIME[0]

        return routes, luminosity


def make_costtable(forbidden):
    global coord
    off_peak = [['' for j in range(len(coord))] for i in range(len(coord))]
    peak = [['' for j in range(len(coord))] for i in range(len(coord))]
    for i in range(len(coord)-1):
        for j in range(i+1, len(coord)):
            off_peak[i][j] = calc_EUCdistance(coord[i], coord[j])
            if j % 2 == 1:
                off_peak[j][i] = calc_EUCdistance(coord[j], coord[i]) * 1.2
            else:
                off_peak[j][i] = calc_EUCdistance(coord[j], coord[i]) * 0.8
    for i in range(len(coord)-1):
        for j in range(i+1, len(coord)):
            peak[i][j] = calc_EUCdistance(coord[i], coord[j]) * 1.3
            if j % 2 == 1:
                peak[j][i] = calc_EUCdistance(coord[j], coord[i]) * 1.2 * 1.2
            else:
                peak[j][i] = calc_EUCdistance(coord[j], coord[i]) * 0.8 * 1.4

    for forb in forbidden:
        off_peak[forb[0]][forb[1]] = 200000
        peak[forb[0]][forb[1]] = 200000

    return off_peak, peak

def insertion_function(a, b, gamma, iteration): #a moves. a, b:firefly
    a2 = [customer for cluster in a.tour for customer in cluster]
    b2 = [customer for cluster in b.tour for customer in cluster]
    #customer
    customer_d = distance.hamming(a2, b2)
    customer_n = int(customer_d * gamma ** iteration)
    # customer_n = distance.hamming(a.routes, b.routes)
    if customer_n <= 2:
        customer_n = 2
    else:
        customer_n = np.random.randint(2, customer_n)
    #cluster
    cluster_d = distance.hamming(a.tour2routes, b.tour2routes)
    cluster_n = 0
    if cluster_d != 0:
        cluster_n = np.random.randint(0, cluster_d)

    acopy = copy.deepcopy(a)
    best_firefly = copy.deepcopy(a)

    for i in range(cluster_n):#cluster insertion
        rand_from = np.random.randint(0, len(acopy.tour2routes))
        rand_into = np.random.randint(0, len(acopy.tour2routes))
        insert_elm = acopy.tour2routes.pop(rand_from)
        acopy.tour2routes.insert(rand_into, insert_elm)
        acopy.update(acopy.tour, acopy.tour2routes)
        if acopy.luminosity < best_firefly.luminosity:
            best_firefly = copy.deepcopy(acopy)
    for i in range(customer_n):#customer insertion
        rand_cluster = np.random.randint(0, len(acopy.tour))
        rand_from = np.random.randint(0, len(acopy.tour[0]))
        rand_into = np.random.randint(0, len(acopy.tour[0]))
        insert_elm = acopy.tour[rand_cluster].pop(rand_from)
        acopy.tour[rand_cluster].insert(rand_into, insert_elm)
        acopy.update(acopy.tour, acopy.tour2routes)
        if acopy.luminosity < best_firefly.luminosity:
            best_firefly = copy.deepcopy(acopy)

    return best_firefly.tour, best_firefly.tour2routes

def beta_step(a, b, gamma, delta):#a, b: class Firefly
    a_tour = [a.tour[cluster] for cluster in a.tour2routes]
    b_tour = [b.tour[cluster] for cluster in b.tour2routes]
    a2 = [customer for cluster in a_tour for customer in cluster]
    b2 = [customer for cluster in b_tour for customer in cluster]
    cluster_d = distance.hamming(a2, b2)
    cluster_beta = 1 / (1 + delta * cluster_d * cluster_d)
    customer_d = distance.hamming(a2, b2)
    customer_beta = 1 / (1 + gamma * customer_d * customer_d)
    cluster_dic = {cluster:'NOT_VISIT' for cluster in a.tour2routes}
    customer_dic = {customer:'NOT_VISIT' for customer in a2}

    new_t2r = ['' for i in range(len(a.tour2routes))]
    new_tour = [['' for j in cluster] for cluster in a_tour]

    idx_t2r = [i for i in range(len(a.tour2routes))]
    idx_tour = [[j for j in range(len(a_tour[0]))] for i in range(len(a_tour))]
    insert_t2r = [elm for elm in a.tour2routes]
    insert_tour = [[i*len(a_tour[0])+j+1 for j in range(len(a_tour[0]))] for i in range(len(a_tour))]
    # print(insert_tour)

    for i in range(len(a.tour2routes)):
        if a.tour2routes[i] == b.tour2routes[i]:
            new_t2r[i] = a.tour2routes[i]
            cluster_dic[new_t2r[i]] = 'VISITED'
            idx_t2r.remove(i)
            insert_t2r.remove(a.tour2routes[i])
    for i in range(len(a_tour)):
        for j in range(len(a_tour[0])):
            if a_tour[i][j] == b_tour[i][j]:
                new_tour[a.tour2routes[i]][j] = a_tour[i][j]
                customer_dic[new_tour[a.tour2routes[i]][j]] = 'VISITED'
                idx_tour[a.tour2routes[i]].remove(j)
                insert_tour[a.tour2routes[i]].remove(a_tour[i][j])

    np.random.shuffle(idx_t2r)
    for i in range(len(idx_tour)):
        np.random.shuffle(idx_tour[i])

    for idx in idx_t2r:
        if np.random.rand() < cluster_beta:
            if cluster_dic[b.tour2routes[idx]] == 'NOT_VISIT':
                new_t2r[idx] = b.tour2routes[idx]
                cluster_dic[b.tour2routes[idx]] = 'VISITED'
                insert_t2r.remove(b.tour2routes[idx])
            elif cluster_dic[a.tour2routes[idx]] == 'NOT_VISIT':
                new_t2r[idx] = a.tour2routes[idx]
                cluster_dic[a.tour2routes[idx]] = 'VISITED'
                insert_t2r.remove(a.tour2routes[idx])
        else:
            if cluster_dic[a.tour2routes[idx]] == 'NOT_VISIT':
                new_t2r[idx] = a.tour2routes[idx]
                cluster_dic[a.tour2routes[idx]] = 'VISITED'
                insert_t2r.remove(a.tour2routes[idx])
            elif cluster_dic[b.tour2routes[idx]] == 'NOT_VISIT':
                new_t2r[idx] = b.tour2routes[idx]
                cluster_dic[b.tour2routes[idx]] = 'VISITED'
                insert_t2r.remove(b.tour2routes[idx])
    for i, idx_cluster in enumerate(idx_tour):
        for idx in idx_cluster:
            if np.random.rand() < customer_beta:
                if customer_dic[b.tour[i][idx]] == 'NOT_VISIT':
                    new_tour[i][idx] = b.tour[i][idx]
                    customer_dic[b.tour[i][idx]] = 'VISITED'
                    insert_tour[i].remove(b.tour[i][idx])
                elif customer_dic[a.tour[i][idx]] == 'NOT_VISIT':
                    new_tour[i][idx] = a.tour[i][idx]
                    customer_dic[a.tour[i][idx]] = 'VISITED'
                    insert_tour[i].remove(a.tour[i][idx])
            else:
                if customer_dic[a.tour[i][idx]] == 'NOT_VISIT':
                    new_tour[i][idx] = a.tour[i][idx]
                    customer_dic[a.tour[i][idx]] = 'VISITED'
                    insert_tour[i].remove(a.tour[i][idx])
                elif customer_dic[b.tour[i][idx]] == 'NOT_VISIT':
                    new_tour[i][idx] = b.tour[i][idx]
                    customer_dic[b.tour[i][idx]] = 'VISITED'
                    insert_tour[i].remove(b.tour[i][idx])

    for i in range(len(insert_tour)):
        np.random.shuffle(insert_tour[i])
    for cluster in insert_t2r:
        idx = new_t2r.index('')
        new_t2r[idx] = cluster
    for i, cluster in enumerate(insert_tour):
        for customer in cluster:
            idx = new_tour[i].index('')
            new_tour[i][idx] = customer

    return new_tour, new_t2r

def alpha_step1(tour, tour2routes, alpha): #a:firefly
    a = Firefly(tour)
    a.update(tour, tour2routes)
    cluster_n = len(a.tour)
    customers_per_cluster_n = len(a.tour[0])

    if a.luminosity < 200000:
        feasible = True
    else:
        feasible = False
    i=0
    z = np.random.randint(0, cluster_n)
    while i < alpha:
        x = np.random.randint(0, customers_per_cluster_n)
        y = np.random.randint(0, customers_per_cluster_n)
        a.tour[z][x], a.tour[z][y] = a.tour[z][y], a.tour[z][x]
        a.update(a.tour, a.tour2routes)
        if a.luminosity > 200000 and feasible == True:
            a.tour[z][x], a.tour[z][y] = a.tour[z][y], a.tour[z][x]
            i-=1
        i+=1

    return a.tour

def firefly_algorithm(**kwargs):
    if kwargs['p']:
        print(kwargs)
    global coord, off_peak, peak, clustered_demand
    coord, forbidden, cluster, demand = extract_xmldata(kwargs['bmark'])
    off_peak, peak = make_costtable(forbidden)
    customers_per_cluster = (len(coord)-1) // (len(cluster)-1)
    tour = [[customers_per_cluster * i + j for j in range(1, customers_per_cluster+1)] for i in range(len(cluster)-1)]
    clustered_demand = [0 for i in range(len(cluster))]
    for i, cluster in enumerate(tour):
        for customer in cluster:
            clustered_demand[i+1] += demand[customer]

    swarm = [Firefly(tour) for i in range(kwargs['f'])]
    swarm = sorted(swarm, key = lambda swarm:swarm.luminosity)
    best_firefly = copy.deepcopy(swarm[0])
    # for fly in swarm:
    #     if fly.luminosity < best_firefly.luminosity:
    #         best_firefly = copy.deepcopy(fly)
    if kwargs['p'] == 1:
        print("Best firefly init: ", best_firefly.luminosity)
    stag_count = 0
    iteration = 0
    NUM_CUSTOMER = len(coord)-1
    start_time = time.time()

    # print([s.luminosity for s in swarm])

    # while stag_count < (NUM_CUSTOMER+1/2*NUM_CUSTOMER*(NUM_CUSTOMER+1)):#the number of customers(N) + Σ(k=1, N)k
    while stag_count < NUM_CUSTOMER*10:
        time1 = time.time()
        for i in range(kwargs['f']):
            for j in range(kwargs['f']):
                if swarm[j].luminosity < swarm[i].luminosity:
                    # new_tour, new_tour2routes = insertion_function(swarm[i], swarm[j], kwargs['g'], iteration)
                    new_tour, new_tour2routes = beta_step(swarm[i], swarm[j], kwargs['g'], kwargs['dlt'])
                    if kwargs['v'] == 1:
                        new_tour = alpha_step1(swarm[i].tour, swarm[i].tour2routes, kwargs['a'])
                    swarm[i].update(new_tour, new_tour2routes)
        swarm = sorted(swarm, key = lambda swarm:swarm.luminosity)
        if swarm[0].luminosity == swarm[-1].luminosity: #all firefly at the same point
            if kwargs['p'] == 1:
                print("*** swarm blocked ***")
            for i in range(1, len(swarm)):
                if kwargs['v'] == 1:
                    new_tour = alpha_step1(swarm[i].tour, swarm[i].tour2routes, kwargs['a'])
                swarm[i].update(new_tour, swarm[i].tour2routes)
        swarm = sorted(swarm, key = lambda swarm:swarm.luminosity)
        time2 = time.time()
        if swarm[0].luminosity < best_firefly.luminosity:
            best_firefly = copy.deepcopy(swarm[0])
            stag_count = 0
        else:
            stag_count += 1
        # for fly in swarm:
        #     if fly.luminosity < best_firefly.luminosity:
        #         best_firefly = copy.deepcopy(fly)
        #         stag_count = 0
        # stag_count += 1
        if iteration % 100 == 0:
            if kwargs['p'] == 1:
                print("")
                print("Iteration: ", iteration)
                print("Swarm: ", [s.luminosity for s in swarm])
                print("Best firefly: ", best_firefly.luminosity)
                # for fly in swarm:
                #     print(fly.routes)
                #     print(fly.luminosity)
            with open('{}'.format(kwargs['fname']), 'a') as f:
                f.write("i:{}\t{}\n".format(iteration, best_firefly.luminosity))
        iteration += 1
        # print("time2-1: {}".format(time2 - time1))
        # print("time3-2: {}".format(time3 - time2))
    end_time = time.time()
    print("Elapsed time: {}\n".format(end_time - start_time))
    with open("{}".format(kwargs['fname']), 'a') as f:
        f.write("Elapsed time: {}\n\n".format(end_time - start_time))

    return best_firefly


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-bmark', type = str, default = "Osaba_data/Osaba_50_1_1.xml", help = "benchmark xml_file name")
    parser.add_argument('-f', type = int, default = 100, help = "the number of firefly")
    parser.add_argument('-a', type = int, default = 1, help = "alpha step parameter")
    parser.add_argument('-g', type = float, default = 0.90, help = "insert customer rate")
    parser.add_argument('-dlt', type = float, default = 1.0, help = "insert cluster rate")
    parser.add_argument('-v', type = int, default = 1, help = "alpha step version")
    parser.add_argument('-p', type = int, default = 1, help = "vorbose information")
    parser.add_argument('-fname', type = str, default = 'vrp/result', help = "save file name")
    args = parser.parse_args()

    if os.path.exists('{}'.format(args.fname)):
        if confirm_input(args.fname):
            with open('{}'.format(args.fname), 'w') as f:
                print("clear previous text")

    while(True):
        aparam = np.random.randint(1,8)
        gparam = (0.01-0.00001)*np.random.rand()+0.00001
        fparam = np.random.randint(20,80)
        with open('{}'.format(args.fname), 'a') as f:
            f.write('-a={}, -g={}, -f={}\n'.format(aparam, gparam, fparam))
        firefly = firefly_algorithm(bmark=args.bmark, f=fparam, a=aparam, g=gparam, dlt=args.dlt, v=args.v, p=args.p, fname=args.fname)
    # firefly = firefly_algorithm(bmark=args.bmark, f=args.f, a=args.a, g=args.g, dlt=args.dlt, p=args.p, fname=args.fname)

    print(firefly.luminosity)
    print(firefly.routes)

    with open('{}'.format(args.fname), 'a') as f:
        f.write("{}\n\n".format(firefly.routes))
    # print(customers)


    # print(coord)
    # a = [1,5,3,2,4,1,6,6,3,3,3,3,3,3]
    # b = [1,5,2,6,3,1,6,5,5,5,5,5,5,5]
    # print(beta_step(a,b,1,0.95,1))
