#cython: profile=True

import argparse
import copy
import cProfile
import distance
import math
import numpy as np
import sys
import os
import time
import xml.etree.ElementTree as ET

from libcpp.vector cimport vector

cdef extern from '<algorithm>' namespace 'std':
    iter std_find 'std::find' [iter, T](iter first, iter last, const T& value)

cdef vector[int] elm_remove(vector[int] a, int elm):
    a.erase(std_find[vector[int].iterator, int](a.begin(), a.end(), elm))
    return a

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


cdef class Firefly:
    cdef:
        int VEHICLE_CAPACITY
        vector[int] DELIVERY_TIME, PEAK_TIME
        public double luminosity
        public vector[int] tour2routes, routes
        public vector[vector[int]] tour
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
    cpdef void update(self, vector[vector[int]] tour, vector[int] tour2routes):
        cdef double luminosity
        luminosity = self.evaluate(tour, tour2routes)
        self.tour = tour
        self.tour2routes = tour2routes
        self.luminosity = luminosity
    cdef double evaluate(self, vector[vector[int]] tour, vector[int] tour2routes):
        """
        tour: the permutation of customers in clusters
        and
        routes: the permutation of customers separated by zero
        If routes is coming, this function converts tour into routes.
        """
        global off_peak, peak, clustered_demand
        cdef:
            unsigned int i
            double triptime, luminosity
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
        self.routes = routes

        cdef size_t routes_size=len(routes)
        luminosity = 0
        triptime = <double>self.DELIVERY_TIME[0]
        for i in range(routes_size-1):
            if routes[i] == 0:
                if triptime != np.inf and <double>self.DELIVERY_TIME[1] < triptime:
                    luminosity = 200000
                luminosity += triptime - <double>self.DELIVERY_TIME[0]
                triptime = <double>self.DELIVERY_TIME[0]
            if <double>self.PEAK_TIME[0] <= triptime and triptime <= <double>self.PEAK_TIME[1]:
                triptime += peak[routes[i]][routes[i+1]]
            else:
                triptime += off_peak[routes[i]][routes[i+1]]
        luminosity += triptime - <double>self.DELIVERY_TIME[0]

        return luminosity


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

def beta_step(Firefly a not None, Firefly b not None, double gamma, double delta):#a, b: class Firefly
    cdef:
        int i, j, cluster_num, customer
        int cluster_size = len(a.tour)
        int customer_size = len(a.tour[0])
        vector[int] cluster, a2, b2, new_t2r, idx_t2r, insert_t2r
        vector[vector[int]] a_tour, b_tour, new_tour, idx_tour, insert_tour
        vector[int] a_t2r = a.tour2routes
        vector[int] b_t2r = b.tour2routes
        vector[vector[int]] a_tourv = a.tour
        vector[vector[int]] b_tourv = b.tour
        int cluster_d, customer_d
        double cluster_beta, customer_beta

    a_tour = [a_tourv[cluster_num] for cluster_num in a_t2r]
    b_tour = [b_tourv[cluster_num] for cluster_num in b_t2r]
    a2 = [customer for cluster in a_tour for customer in cluster]
    b2 = [customer for cluster in b_tour for customer in cluster]
    cluster_d = distance.hamming(a_t2r, b_t2r)
    cluster_beta = 1 / (1 + delta * cluster_d)
    customer_d = distance.hamming(a2, b2)
    customer_beta = 1 / (1 + gamma * customer_d * customer_d)
    cluster_dic = {cluster_num:'NOT_VISIT' for cluster_num in a_t2r}
    customer_dic = {customer:'NOT_VISIT' for customer in a2}

    new_t2r = [0 for i in range(cluster_size)]
    new_tour = [[0 for j in cluster] for cluster in a_tour]

    idx_t2r = [i for i in range(cluster_size)]
    idx_tour = [[j for j in range(customer_size)] for i in range(cluster_size)]
    insert_t2r = [elm for elm in a_t2r]
    insert_tour = [[i*customer_size+j+1 for j in range(customer_size)] for i in range(cluster_size)]

    for i in range(cluster_size):
        if a_t2r[i] == b_t2r[i]:
            new_t2r[i] = a_t2r[i]
            cluster_dic[new_t2r[i]] = 'VISITED'
            idx_t2r = elm_remove(idx_t2r, i)
            insert_t2r = elm_remove(insert_t2r, new_t2r[i])
    for i in range(cluster_size):
        for j in range(customer_size):
            if a_tour[i][j] == b_tour[i][j]:
                new_tour[a_t2r[i]][j] = a_tour[i][j]
                customer_dic[new_tour[a_t2r[i]][j]] = 'VISITED'
                idx_tour[a_t2r[i]] = elm_remove(idx_tour[a_t2r[i]], j)
                insert_tour[a_t2r[i]] = elm_remove(insert_tour[a_t2r[i]], new_tour[a_t2r[i]][j])

    np.random.shuffle(idx_t2r)
    for i in range(cluster_size):
        np.random.shuffle(idx_tour[i])

    for i in range(cluster_size):
        if np.random.rand() < cluster_beta:
            if cluster_dic[b_t2r[idx_t2r[i]]] is 'NOT_VISIT':
                new_t2r[idx_t2r[i]] = b_t2r[idx_t2r[i]]
                cluster_dic[new_t2r[idx_t2r[i]]] = 'VISITED'
                insert_t2r = elm_remove(insert_t2r, new_t2r[idx_t2r[i]])
            elif cluster_dic[a_t2r[idx_t2r[i]]] is 'NOT_VISIT':
                new_t2r[idx_t2r[i]] = a_t2r[idx_t2r[i]]
                cluster_dic[a_t2r[idx_t2r[i]]] = 'VISITED'
                insert_t2r = elm_remove(insert_t2r, new_t2r[idx_t2r[i]])
        else:
            if cluster_dic[a_t2r[idx_t2r[i]]] is 'NOT_VISIT':
                new_t2r[idx_t2r[i]] = a_t2r[idx_t2r[i]]
                cluster_dic[a_t2r[idx_t2r[i]]] = 'VISITED'
                insert_t2r = elm_remove(insert_t2r, new_t2r[idx_t2r[i]])
            elif cluster_dic[b_t2r[idx_t2r[i]]] is 'NOT_VISIT':
                new_t2r[idx_t2r[i]] = b_t2r[idx_t2r[i]]
                cluster_dic[b_t2r[idx_t2r[i]]] = 'VISITED'
                insert_t2r = elm_remove(insert_t2r, new_t2r[idx_t2r[i]])

    for i in range(cluster_size):
        for idx in idx_tour[i]:
            if np.random.rand() < customer_beta:
                if customer_dic[b_tourv[i][idx]] is 'NOT_VISIT':
                    new_tour[i][idx] = b_tourv[i][idx]
                    customer_dic[b_tourv[i][idx]] = 'VISITED'
                    insert_tour[i] = elm_remove(insert_tour[i], new_tour[i][idx])
                elif customer_dic[a_tourv[i][idx]] is 'NOT_VISIT':
                    new_tour[i][idx] = a_tourv[i][idx]
                    customer_dic[a_tourv[i][idx]] = 'VISITED'
                    insert_tour[i] = elm_remove(insert_tour[i], new_tour[i][idx])
            else:
                if customer_dic[a_tourv[i][idx]] is 'NOT_VISIT':
                    new_tour[i][idx] = a_tourv[i][idx]
                    customer_dic[a_tourv[i][idx]] = 'VISITED'
                    insert_tour[i] = elm_remove(insert_tour[i], new_tour[i][idx])
                elif customer_dic[b_tourv[i][idx]] is 'NOT_VISIT':
                    new_tour[i][idx] = b_tourv[i][idx]
                    customer_dic[b_tourv[i][idx]] = 'VISITED'
                    insert_tour[i] = elm_remove(insert_tour[i], new_tour[i][idx])

    cdef:
        int int2r_size = len(insert_t2r), intour_size
    for i in range(cluster_size):
        np.random.shuffle(insert_tour[i])
    for i in range(int2r_size):
        new_t2r.insert(std_find[vector[int].iterator, int](new_t2r.begin(), new_t2r.end(), 0), insert_t2r[i])
    for i in range(cluster_size):
        intour_size = len(insert_tour[i])
        for j in range(intour_size):
            new_tour[i].insert(std_find[vector[int].iterator, int](new_tour[i].begin(), new_tour[i].end(), 0), insert_tour[i][j])

    return new_tour, new_t2r

def alpha_step1(Firefly a not None, int alpha): #a:firefly
    cdef:
        int i=0, x, y, z
        int cluster_size=len(a.tour), customers_size=len(a.tour2routes)
        bint feasible

    if a.luminosity < 200000:
        feasible = True
    else:
        feasible = False
    #cluster_alpha = np.random.randint(1, 2)
    #while i < cluster_alpha:
    #    x = np.random.randint(0, cluster_size)
    #    y = np.random.randint(0, cluster_size)
    #    a.tour2routes[x], a.tour2routes[y] = a.tour2routes[y], a.tour2routes[x]
    #    a.update(a.tour, a.tour2routes)
    #    if a.luminosity > 200000 and feasible == True:
    #        a.tour2routes[x], a.tour2routes[y] = a.tour2routes[y], a.tour2routes[x]
    #    i+=1
    z = np.random.randint(0, cluster_size)
    while i < alpha:
        x = np.random.randint(0, customers_size)
        y = np.random.randint(0, customers_size)
        a.tour[z][x], a.tour[z][y] = a.tour[z][y], a.tour[z][x]
        a.update(a.tour, a.tour2routes)
        if a.luminosity > 200000 and feasible == True:
            a.tour[z][x], a.tour[z][y] = a.tour[z][y], a.tour[z][x]
            i-=1
        i+=1

    return a.tour, a.tour2routes

def firefly_algorithm(dict kwargs):
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
    #LIMIT = 2000
    start_time = time.time()
    #print(LIMIT)

    while stag_count < NUM_CUSTOMER*10:
    #while stag_count < LIMIT:#the number of customers(N) + Σ(k=1, N)k
        time1 = time.time()
        for i in range(kwargs['f']):
            for j in range(kwargs['f']):
                if swarm[j].luminosity < swarm[i].luminosity:
                    # new_tour, new_tour2routes = insertion_function(swarm[i], swarm[j], kwargs['g'], iteration)
                    new_tour, new_tour2routes = beta_step(swarm[i], swarm[j], kwargs['g'], kwargs['dlt'])
                    if kwargs['v'] == 1:
                        new_tour, new_tour2routes = alpha_step1(swarm[i], kwargs['a'])
                    swarm[i].update(new_tour, new_tour2routes)
        swarm = sorted(swarm, key = lambda swarm:swarm.luminosity)
        if swarm[0].luminosity == swarm[-1].luminosity: #all firefly at the same point
            if kwargs['p'] == 1:
                print("*** swarm blocked ***")
            for i in range(1, len(swarm)):
                if kwargs['v'] == 1:
                    new_tour, new_tour2routes = alpha_step1(swarm[i], kwargs['a'])
                swarm[i].update(new_tour, new_tour2routes)
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
            # with open('{}'.format(kwargs['fname']), 'a') as f:
            #     f.write("i:{}\t{}\n".format(iteration, best_firefly.luminosity))
        iteration += 1
        # print("time2-1: {}".format(time2 - time1))
        # print("time3-2: {}".format(time3 - time2))
    end_time = time.time()
    print("Elapsed time: {}\n".format(end_time - start_time))
    # with open("{}".format(kwargs['fname']), 'a') as f:
    #     f.write("Elapsed time: {}\n\n".format(end_time - start_time))

    print(best_firefly.routes)
    return best_firefly
