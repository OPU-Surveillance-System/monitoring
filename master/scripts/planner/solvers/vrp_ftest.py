import argparse
import copy
import cProfile
import distance
import math
import numpy as np
import os
import pickle
import re
import sys
import scipy
import scipy.stats
import scipy.optimize
import time
import utm
import xml.etree.ElementTree as ET
# import pymc3

from plot_kinds import plot_beta

import folium
from folium.plugins.beautify_icon import BeautifyIcon
from plot_path import make_pathline

FORB_COST = 200000
TIME_WINDOW = [6*60*60, 15*60*60]
PEAK_TIME = [8*60*60, 10*60*60]

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
    # demand = [dem_ent[i] + dem_rec[i] for i in range(len(dem_ent))]

    return coord, forbidden, cluster, dem_ent, dem_rec

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

    # def get_hdi(self):
    #     """
    #     Compute the Highest Density Interval of the team's distribution:
    #     Adapted from: https://stackoverflow.com/questions/22284502/highest-posterior-density-region-and-central-credible-region
    #     """
    #     inconfidence_mass = 1 - self.confidence_mass
    #
    #     def get_interval_width(low_tail):
    #         interval_width = self.distrib.ppf(self.confidence_mass + low_tail) - self.distrib.ppf(low_tail)
    #
    #         return interval_width
    #
    #     hdi_low_tail = scipy.optimize.fmin(get_interval_width, inconfidence_mass, ftol=1e-8, disp=False)[0]
    #     hdi = self.distrib.ppf([hdi_low_tail, self.confidence_mass + hdi_low_tail])
    #
    #     return hdi

    def get_hdi(self):
        return pymc3.stats.hpd(self.distrib.rvs(size=10000)).tolist()

    def update(self, n, z):
        """
        Update the Beta distribution:
            n: number of fireflyAlgorithm runs
            z: number of osaba > ours (ours is better than osaba)
        """
        self.a += z
        self.b += n - z
        self.distrib = scipy.stats.beta(self.a, self.b)
        self.hdi = self.get_hdi()

class Firefly:
    def __init__(self, tour, capacity):
        self.VEHICLE_CAPACITY = capacity
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
        global off_peak, peak, clustered_dem_ent
        prob_size = len(tour)*len(tour[0])
        routes = ['' for i in range(prob_size+len(tour)+1)]
        routes[0] = 0
        routes_i = 1
        load_amount = 0
        customer_size = len(tour[0])
        continuous_i = False
        triptime = TIME_WINDOW[0]
        time_exceed = False
        luminosity = 0
        for cluster in tour2routes:
            if cluster != tour2routes[0]:## if not the first loop
                if time_exceed != False or self.VEHICLE_CAPACITY < load_amount + clustered_dem_ent[cluster]:
                    routes[routes_i] = 0
                    if time_exceed == 'peak':
                        luminosity += (triptime-TIME_WINDOW[0]) + peak[routes[routes_i-1]][routes[routes_i]]
                    else:
                        luminosity += (triptime-TIME_WINDOW[0]) + off_peak[routes[routes_i-1]][routes[routes_i]]
                    routes_i += 1
                    continuous_i = False
                    certified_triptime = 0
                    triptime = TIME_WINDOW[0]
                    time_exceed = False
                    load_amount = clustered_dem_ent[cluster]
                else:
                    load_amount += clustered_dem_ent[cluster]
                    continuous_i = routes_i
                    certified_triptime = triptime
            else:
                load_amount = clustered_dem_ent[cluster]
            for customer_i in range(customer_size):
                routes[routes_i] = tour[cluster][customer_i]
                if PEAK_TIME[0] <= triptime and triptime <= PEAK_TIME[1]:
                    triptime += peak[routes[routes_i-1]][routes[routes_i]]
                else:
                    triptime += off_peak[routes[routes_i-1]][routes[routes_i]]
                routes_i+=1
                if TIME_WINDOW[1] < triptime and continuous_i != False:
                    routes, luminosity, triptime = insert0_reeval(routes, routes_i, continuous_i, luminosity, certified_triptime)
                    routes_i += 1
                    certified_triptime = 0
                    continuous_i = False
                    load_amount = clustered_dem_ent[cluster]
                if customer_i == customer_size-1:
                    if PEAK_TIME[0] <= triptime and triptime <= PEAK_TIME[1]:
                        if TIME_WINDOW[1] < triptime + peak[routes[routes_i-1]][0]:
                            if continuous_i != False:
                                routes, luminosity, triptime = insert0_reeval(routes, routes_i, continuous_i, luminosity, certified_triptime)
                                routes_i+=1
                                certified_triptime = 0
                                continuous_i = False
                                load_amount = clustered_dem_ent[cluster]
                                if PEAK_TIME[0] <= triptime and triptime <= PEAK_TIME[1]:
                                    if TIME_WINDOW[1] < triptime + peak[routes[routes_i-1]][0]:
                                        time_exceed = 'peak'
                                else:
                                    if TIME_WINDOW[1] < triptime + off_peak[routes[routes_i-1]][0]:
                                        time_exceed = 'off_peak'
                            else:
                                time_exceed = 'peak'
                    else:
                        if TIME_WINDOW[1] < triptime + off_peak[routes[routes_i-1]][0]:
                            if continuous_i != False:
                                routes, luminosity, triptime = insert0_reeval(routes, routes_i, continuous_i, luminosity, certified_triptime)
                                routes_i+=1
                                certified_triptime = 0
                                continuous_i = False
                                load_amount = clustered_dem_ent[cluster]
                                if PEAK_TIME[0] <= triptime and triptime <= PEAK_TIME[1]:
                                    if TIME_WINDOW[1] < triptime + peak[routes[routes_i-1]][0]:
                                        time_exceed = 'peak'
                                else:
                                    if TIME_WINDOW[1] < triptime + off_peak[routes[routes_i-1]][0]:
                                        time_exceed = 'off_peak'
                            else:
                                time_exceed = 'off_peak'
        routes[routes_i] = 0
        if PEAK_TIME[0] <= triptime and triptime <= PEAK_TIME[1]:
            luminosity += (triptime-TIME_WINDOW[0]) + peak[routes[routes_i-1]][routes[routes_i]]
        else:
            luminosity += (triptime-TIME_WINDOW[0]) + off_peak[routes[routes_i-1]][routes[routes_i]]

        routes = list(filter(lambda str:str != '', routes))

        return routes, luminosity

#insert 0 into ahead of last cluster, and reevaluate triptime
def insert0_reeval(routes, routes_i, continuous_i, luminosity, certified_triptime):
    global peak, off_peak
    routes.insert(continuous_i, 0)
    triptime = TIME_WINDOW[0]
    if PEAK_TIME[0] <= certified_triptime and certified_triptime <= PEAK_TIME[1]:
        luminosity += (certified_triptime-TIME_WINDOW[0]) + peak[routes[continuous_i-1]][routes[continuous_i]]
    else:
        luminosity += (certified_triptime-TIME_WINDOW[0]) + off_peak[routes[continuous_i-1]][routes[continuous_i]]
    for i in range(continuous_i, routes_i):
        if PEAK_TIME[0] <= triptime and triptime <= PEAK_TIME[1]:
            triptime += peak[routes[i]][routes[i+1]]
        else:
            triptime += off_peak[routes[i]][routes[i+1]]

    return routes, luminosity, triptime

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
        off_peak[forb[0]][forb[1]] = FORB_COST
        peak[forb[0]][forb[1]] = FORB_COST

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
    a2 = [customer for cluster in a.tour for customer in cluster]
    b2 = [customer for cluster in b.tour for customer in cluster]
    cluster_d = distance.hamming(a.tour2routes, b.tour2routes)
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

    for i in reversed(idx_t2r):
        if a.tour2routes[i] == b.tour2routes[i]:
            new_t2r[i] = a.tour2routes[i]
            cluster_dic[new_t2r[i]] = 'VISITED'
            idx_t2r.remove(i)
            insert_t2r.remove(new_t2r[i])
    for i in a.tour2routes:
        for j in reversed(idx_tour[i]):
            if a.tour[i][j] == b.tour[i][j]:
                new_tour[i][j] = a.tour[i][j]
                customer_dic[new_tour[i][j]] = 'VISITED'
                idx_tour[i].remove(j)
                insert_tour[i].remove(new_tour[i][j])

    np.random.shuffle(idx_t2r)
    for i in range(len(idx_tour)):
        np.random.shuffle(idx_tour[i])

    for idx in reversed(idx_t2r):
        if np.random.rand() < cluster_beta:
            if cluster_dic[b.tour2routes[idx]] == 'NOT_VISIT':
                new_t2r[idx] = b.tour2routes[idx]
                cluster_dic[new_t2r[idx]] = 'VISITED'
                idx_t2r.remove(idx)
                insert_t2r.remove(new_t2r[idx])
            elif cluster_dic[a.tour2routes[idx]] == 'NOT_VISIT':
                new_t2r[idx] = a.tour2routes[idx]
                cluster_dic[new_t2r[idx]] = 'VISITED'
                idx_t2r.remove(idx)
                insert_t2r.remove(new_t2r[idx])
        else:
            if cluster_dic[a.tour2routes[idx]] == 'NOT_VISIT':
                new_t2r[idx] = a.tour2routes[idx]
                cluster_dic[new_t2r[idx]] = 'VISITED'
                idx_t2r.remove(idx)
                insert_t2r.remove(new_t2r[idx])
            elif cluster_dic[b.tour2routes[idx]] == 'NOT_VISIT':
                new_t2r[idx] = b.tour2routes[idx]
                cluster_dic[new_t2r[idx]] = 'VISITED'
                idx_t2r.remove(idx)
                insert_t2r.remove(new_t2r[idx])
    for i, idx_cluster in enumerate(idx_tour):
        for j in reversed(idx_cluster):
            if np.random.rand() < customer_beta:
                if customer_dic[b.tour[i][j]] == 'NOT_VISIT':
                    new_tour[i][j] = b.tour[i][j]
                    customer_dic[new_tour[i][j]] = 'VISITED'
                    idx_cluster.remove(j)
                    insert_tour[i].remove(new_tour[i][j])
                elif customer_dic[a.tour[i][j]] == 'NOT_VISIT':
                    new_tour[i][j] = a.tour[i][j]
                    customer_dic[new_tour[i][j]] = 'VISITED'
                    idx_cluster.remove(j)
                    insert_tour[i].remove(new_tour[i][j])
            else:
                if customer_dic[a.tour[i][j]] == 'NOT_VISIT':
                    new_tour[i][j] = a.tour[i][j]
                    customer_dic[new_tour[i][j]] = 'VISITED'
                    idx_cluster.remove(j)
                    insert_tour[i].remove(new_tour[i][j])
                elif customer_dic[b.tour[i][j]] == 'NOT_VISIT':
                    new_tour[i][j] = b.tour[i][j]
                    customer_dic[new_tour[i][j]] = 'VISITED'
                    idx_cluster.remove(j)
                    insert_tour[i].remove(new_tour[i][j])

    for i, insert_elm in zip(idx_t2r, insert_t2r):
        new_t2r[i] = insert_elm
    for i in range(len(idx_tour)):
        for j, insert_elm in zip(idx_tour[i], insert_tour[i]):
            new_tour[i][j] = insert_elm

    return new_tour, new_t2r

def alpha_step0(a, alpha):
    """
    mutation on clusters
    """
    cluster_size = len(a.tour)
    ini_luminosity = a.luminosity
    for i in range(alpha):
        x = np.random.randint(0, cluster_size)
        y = np.random.randint(0, cluster_size)
        a.tour2routes[x], a.tour2routes[y] = a.tour2routes[y], a.tour2routes[x]
    a.update(a.tour, a.tour2routes)
    if ini_luminosity < a.luminosity:
        a.tour2routes[x], a.tour2routes[y] = a.tour2routes[y], a.tour2routes[x]

    return a.tour2routes

def alpha_step1(a, alpha): #a:firefly
    global peak #to confirm whether forbidden or not
    cluster_size = len(a.tour)
    customer_size = len(a.tour[0])

    if a.luminosity < FORB_COST:
        feasible = True
    else:
        feasible = False
    i=0
    z = np.random.randint(0, cluster_size)
    while i < alpha:
        x = np.random.randint(0, customer_size)
        y = np.random.randint(0, customer_size)
        a.tour[z][x], a.tour[z][y] = a.tour[z][y], a.tour[z][x]
        for customer_i in range(customer_size-1):
            if peak[a.tour[z][customer_i]][a.tour[z][customer_i+1]] == FORB_COST \
            and feasible == True:#可能解を突然変異で破壊した場合
                a.tour[z][x], a.tour[z][y] = a.tour[z][y], a.tour[z][x]
                i-=1
                break
        i+=1
    return a.tour

def alpha_step2(a, alpha):
    cluster_size = len(a.tour)
    customer_size = len(a.tour[0])
    if customer_size < alpha:
        sys.exit("error: alpha(v2) is lower than the customer size")
    if a.luminosity < FORB_COST:
        feasible = True
    else:
        feasible = False
    while True:
        idxs = [i for i in range(customer_size)]
        np.random.shuffle(idxs)
        x = idxs[0:alpha]
        y = idxs[0:alpha]
        z = np.random.randint(0, cluster_size)
        np.random.shuffle(y)
        for i in range(alpha):
            a.tour[z][x[i]], a.tour[z][y[i]] = a.tour[z][y[i]], a.tour[z][x[i]]
        a.update(a.tour, a.tour2routes)
        if a.luminosity > FORB_COST and feasible == True:
            for i in range(alpha):
                a.tour[z][x[i]], a.tour[z][y[i]] = a.tour[z][y[i]], a.tour[z][x[i]]
            continue
        break
    return a.tour, a.tour2routes

def alpha_step4(a, alpha, t, step, schedule):
    global peak
    cluster_size = len(a.tour)
    customer_size = len(a.tour[0])

    if schedule == "linear":
        segment = len(a.tour[0]) - (t//step)
    elif schedule == "sqrt":
        segment = int(len(a.tour[0]) - (t//step)**(1/2))
    if segment < 2:
        segment = 2
    if a.luminosity < FORB_COST:
        feasible = True
    else:
        feasible = False
    origin = np.random.randint(0, len(a.tour[0]))
    end = origin + segment
    z = np.random.randint(0, len(a.tour))
    i=0
    while i < alpha:
        x = np.random.randint(origin, end+1) % len(a.tour[0])
        y = np.random.randint(origin, end+1) % len(a.tour[0])
        a.tour[z][x], a.tour[z][y] = a.tour[z][y], a.tour[z][x]
        for customer_i in range(customer_size-1):
            if peak[a.tour[z][customer_i]][a.tour[z][customer_i+1]] == FORB_COST \
            and feasible == True:#可能解を突然変異で破壊した場合
                a.tour[z][x], a.tour[z][y] = a.tour[z][y], a.tour[z][x]
                i-=1
                break
        i+=1
    return a.tour

# Alpha step: exploration (v5)
def alpha_step5(a, alpha, t, step, schedule):
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
    return a.tour, a.tour2routes

def firefly_algorithm(run_num, **kwargs):
    if kwargs['p']:
        print(kwargs)
    capa_dict = {"50_1_1":240, "50_1_2":160, "50_1_3":240, "50_1_4":160,
                "50_2_1":240, "50_2_2":160, "50_2_3":240, "50_2_4":160,
                "80_1":240, "80_2":160, "80_3":240, "80_4":160,
                "100_1":160, "100_2":260, "100_3":320}
    probname = re.split("[/.]", kwargs['bmark'])[1].strip('Osaba_')
    if kwargs['v'] == 4 or kwargs['v'] == 5:
        segdir='seg/'
    else:
        segdir='nseg/'
    CAPACITY = capa_dict[probname]
    global coord, off_peak, peak, clustered_dem_ent
    coord, forbidden, cluster, dem_ent, dem_rec = extract_xmldata(kwargs['bmark'])
    off_peak, peak = make_costtable(forbidden)
    customers_per_cluster = (len(coord)-1) // (len(cluster)-1)
    tour = [[customers_per_cluster * i + j for j in range(1, customers_per_cluster+1)] for i in range(len(cluster)-1)]
    clustered_dem_ent = [0 for i in range(len(cluster)-1)]
    for i, cluster in enumerate(tour):
        for customer in cluster:
            clustered_dem_ent[i] += dem_ent[customer]

    swarm = [Firefly(tour, CAPACITY) for i in range(kwargs['f'])]
    swarm = sorted(swarm, key = lambda swarm:swarm.luminosity)

    # swarm.update([[4, 5, 10, 9, 7, 8, 6, 2, 1, 3],[11, 14, 13, 15, 17, 19, 20, 18, 16, 12],[23, 22, 25, 26, 29, 30, 28, 27, 24, 21],[31, 32, 33, 34, 35, 38, 37, 36, 39, 40],[48, 47, 41, 42, 43, 45, 46, 49, 50, 44]],
    #                 [1,2,4,0,3])
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
    best_eachi=[]
    stag_count = 0
    MAX_STAG = (NUM_CUSTOMER+1/2*NUM_CUSTOMER*(NUM_CUSTOMER+1))
    # while stag_count < (NUM_CUSTOMER+1/2*NUM_CUSTOMER*(NUM_CUSTOMER+1)):#the number of customers(N) + Σ(k=1, N)k
    while stag_count < MAX_STAG:
    # while True:
        time1 = time.time()
        for i in range(kwargs['f']):
            if MAX_STAG < stag_count:
                break
            for j in range(kwargs['f']):
                if swarm[j].luminosity < swarm[i].luminosity:
                    # new_tour, new_tour2routes = insertion_function(swarm[i], swarm[j], kwargs['g'], iteration)
                    new_tour, new_tour2routes = beta_step(swarm[i], swarm[j], kwargs['g'], kwargs['dlt'])
                    swarm[i].update(new_tour, new_tour2routes)
                    if swarm[i].luminosity < best_firefly.luminosity:
                        stag_count=0
                        best_firefly = copy.deepcopy(swarm[i])
                    else:
                        stag_count+=1
                        if MAX_STAG < stag_count:
                            break
                    if kwargs['v'] == 1:
                        new_tour = alpha_step1(swarm[i], kwargs['a'])
                    elif kwargs['v'] == 2:
                        new_tour, new_tour2routes = alpha_step2(swarm[i], kwargs['a'])
                    elif kwargs['v'] == 4:
                        new_tour = alpha_step4(swarm[i], kwargs['a'], iteration, kwargs['s'], kwargs['sch'])
                    else:
                        new_tour, new_tour2routes = alpha_step5(swarm[i], kwargs['a'], iteration, kwargs['s'], kwargs['sch'])
                    new_tour2routes = alpha_step0(swarm[i], kwargs['ca'])
                    swarm[i].update(new_tour, new_tour2routes)
                    if swarm[i].luminosity < best_firefly.luminosity:
                        stag_count=0
                        best_firefly = copy.deepcopy(swarm[i])
                    else:
                        stag_count+=1
                        if MAX_STAG < stag_count:
                            break
        if MAX_STAG < stag_count:
            break
        swarm = sorted(swarm, key = lambda swarm:swarm.luminosity)
        if swarm[0].luminosity == swarm[-1].luminosity: #all firefly at the same point
            if kwargs['p'] == 1:
                print("*** swarm blocked ***")
            for i in range(1, len(swarm)):
                if kwargs['v'] == 1:
                    new_tour = alpha_step1(swarm[i], kwargs['a'])
                elif kwargs['v'] == 2:
                    new_tour, new_tour2routes = alpha_step2(swarm[i], kwargs['a'])
                elif kwargs['v'] == 4:
                    new_tour = alpha_step4(swarm[i], kwargs['a'], iteration, kwargs['s'], kwargs['sch'])
                else:
                    new_tour, new_tour2routes = alpha_step5(swarm[i], kwargs['a'], iteration, kwargs['s'], kwargs['sch'])
                new_tour2routes = alpha_step0(swarm[i], kwargs['ca'])
                swarm[i].update(new_tour, new_tour2routes)
                if swarm[i].luminosity < best_firefly.luminosity:
                    stag_count=0
                    best_firefly = copy.deepcopy(swarm[i])
                else:
                    stag_count+=1
                    if MAX_STAG < stag_count:
                        break
        swarm = sorted(swarm, key = lambda swarm:swarm.luminosity)
        time2 = time.time()
        if iteration % 10 == 0:
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
            # make_pathline(best_firefly.routes, kwargs['bmark'], '{}{}{}/i{}'.format(kwargs['hdir'], segdir, probname, iteration))
        # best_eachi.append(best_firefly.luminosity)
        iteration += 1
        # print("time2-1: {}".format(time2 - time1))
        # print("time3-2: {}".format(time3 - time2))
    end_time = time.time()
    # with open('vrp/exp_{}pickle/i700_1.0/{}-{}'.format(segdir, probname, run_num), 'wb') as f:
    #     pickle.dump(best_eachi, f)
    print("\nIteration: {}".format(iteration))
    print("Best firefly: {}".format(best_firefly.luminosity))
    print("Elapsed time: {}\n".format(end_time - start_time))
    # with open("{}".format(kwargs['fname']), 'a') as f:
    #     f.write("routes: {}\n".format(best_firefly.routes))
    # with open("{}".format(kwargs['fname']), 'a') as f:
    #     f.write("best: {}\n".format(best_firefly.luminosity))
    # with open("{}".format(kwargs['fname']), 'a') as f:
    #     f.write("Elapsed time: {}\n\n".format(end_time - start_time))

    # return best_firefly, end_time-start_time
    return best_firefly

#unfinished
def all_bench_run(args):
    benchs = ['Osaba_data/Osaba_50_1_1.xml','Osaba_data/Osaba_50_1_2.xml','Osaba_data/Osaba_50_1_3.xml','Osaba_data/Osaba_50_1_4.xml',
            'Osaba_data/Osaba_50_2_1.xml','Osaba_data/Osaba_50_2_2.xml','Osaba_data/Osaba_50_2_3.xml','Osaba_data/Osaba_50_2_4.xml',
            'Osaba_data/Osaba_80_1.xml','Osaba_data/Osaba_80_2.xml','Osaba_data/Osaba_80_3.xml','Osaba_data/Osaba_80_4.xml',
            'Osaba_data/Osaba_100_1.xml','Osaba_data/Osaba_100_2.xml','Osaba_data/Osaba_100_3.xml']
    # dlts = [3.0, 5.0, 10.0]
    # aparams=[5,8]
    if args.v == 1:
        fname='nseg'
        args.a=4
    elif args.v == 4:
        fname='seg'
        args.a=5
    for bench in benchs:
        args.bmark = bench
        # args.fname = 'vrp/bayes_estimation/{}'.format(fname) + re.split('[./]', bench)[1].strip('Osaba_')
        # args.fname = 'vrp/bayes_estimation/'
        n_times_run(args)
        bayes_estimation(args)

def n_times_run(args):
    n = 10
    with open("{}".format(args.fname), 'w') as f:
        f.write("-g={}, -f={}, -dlt={}, MAX_STAG=(1/2)*N*(N+1), -ca={}, -v={}\n".format(args.g,args.f,args.dlt,args.ca,args.v))
    luminosities=[]
    times=[]
    for i in range(n):
        firefly, t = firefly_algorithm(i, bmark=args.bmark, f=args.f, a=args.a, ca=args.ca, g=args.g, dlt=args.dlt, v=args.v, p=args.p, fname=args.fname, hdir=args.hdir, s=args.s, sch=args.sch)
        luminosities.append(firefly.luminosity)
        times.append(t)
    with open("{}".format(args.fname), 'a') as f:
        f.write("mean: {}\n".format(np.mean(luminosities)))
        f.write("std: {}\n".format(np.std(luminosities)))
        f.write("mean-time: {}\n".format(np.mean(times)))
        f.write("std-time: {}".format(np.std(times)))

def bayes_estimation(args):
    args.bmark=re.split('[/.]',args.bmark)[1].strip('Osaba_')
    if not os.path.exists('{}seg/d{}'.format(args.fname, args.bmark)):
        os.mkdir('{}seg/d{}'.format(args.fname, args.bmark))
    # with open('vrp/bayes_estimation/osaba_results', 'r') as f:
    #     for line in f:
    #         if args.bmark in line:
    #             osaba_best = float(re.split('\t',line)[1].strip())
    # bests=[]
    # with open('{}{}'.format(args.fname, args.bmark), 'r') as f:
    #     for line in f:
    #         if 'best:' in line:
    #             bests.append(float(re.split('[ :]',line)[2].strip()))
    nseg_bests=[]
    with open('{}nseg/{}'.format(args.fname, args.bmark), 'r') as f:
        for line in f:
            if 'best:' in line:
                nseg_bests.append(float(re.split('[ :]',line)[2].strip()))
    seg_bests=[]
    with open('{}seg/{}'.format(args.fname, args.bmark), 'r') as f:
        for line in f:
            if 'best:' in line:
                seg_bests.append(float(re.split('[ :]',line)[2].strip()))

    bayes_binomial = binomial(1, 1, 0.95)
    mean_size=3
    batch_size=10
    dset_try=5
    update_num_per=len(nseg_bests)//mean_size//batch_size
    for k in range(dset_try):
        seg_win=0
        np.random.shuffle(nseg_bests)
        np.random.shuffle(seg_bests)
        for i in range(1, update_num_per*batch_size+1):
            nseg_mean = [nseg_bests[(i-1)*mean_size+j] for j in range(mean_size)]
            nseg_mean = np.mean(nseg_mean)
            seg_mean = [seg_bests[(i-1)*mean_size+j] for j in range(mean_size)]
            seg_mean = np.mean(seg_mean)
            # if osaba_best > mean:
            #     ff_win+=1
            if nseg_mean > seg_mean:
                seg_win+=1
            if i % batch_size == 0:
                print(seg_win, i)
                bayes_binomial.update(batch_size, seg_win)
                plot_beta(bayes_binomial.a, bayes_binomial.b, args.bmark, i//batch_size+k*update_num_per)
                print(i//batch_size+k*update_num_per)
                seg_win=0
                if bayes_binomial.hdi[0] > 0.5:
                    with open('{}seg/d{}/result'.format(args.fname, args.bmark), 'w') as f:
                        f.write('win')
                        return
                elif bayes_binomial.hdi[1] <= 0.5:
                    with open('{}seg/d{}/result'.format(args.fname, args.bmark), 'w') as f:
                        f.write('lose')
                        return
    with open('{}seg/d{}/result'.format(args.fname, args.bmark), 'w') as f:
        f.write('draw')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-bmark', type = str, default = 'Osaba_data/Osaba_50_1_1.xml', help = "benchmark xml_file name")
    parser.add_argument('-f', type = int, default = 50, help = "the number of firefly")
    parser.add_argument('-a', type = int, default = 1, help = "alpha step parameter")
    parser.add_argument('-ca', type = int, default = 1, help = "cluster alpha step parameter")
    parser.add_argument('-g', type = float, default = 0.90, help = "insert customer rate")
    parser.add_argument('-dlt', type = float, default = 1.0, help = "insert cluster rate")
    parser.add_argument('-v', type = int, default = 1, help = "alpha step version")
    parser.add_argument('-p', type = int, default = 1, help = "vorbose information")
    parser.add_argument('-fname', type = str, default = 'vrp/result', help = "save file name")
    parser.add_argument('-hdir', type = str, default = 'vrp/plot_map/', help = "save map_html name")
    parser.add_argument('-s', type = int, default = 1, help = "segment decrease rate")
    parser.add_argument('-sch', type = str, default = 'linear', help = "segment decrease schedule")
    args = parser.parse_args()


    # cProfile.run('firefly_algorithm(bmark=args.bmark, f=args.f, a=args.a, g=args.g, dlt=args.dlt, v=args.v, p=args.p, fname=args.fname)', sort='time')
    if args.v == 4 or args.v == 5:
        segdir='seg/'
    else:
        segdir='nseg/'
    probname = re.split("[/.]", args.bmark)[1].strip('Osaba_')
    if os.path.exists('{}'.format(args.fname)):
        if confirm_input(args.fname):
            with open('{}'.format(args.fname), 'w') as f:
                print("clear previous text")
    # if not os.path.exists('{}{}{}'.format(args.hdir, segdir, probname)):
    #         os.mkdir('{}{}{}'.format(args.hdir, segdir, probname))
    # with open('{}'.format(args.fname), 'a') as f:
    #     f.write("-g={}, -a={}, -f={}\n".format(args.g, args.a, args.f, args.dlt))

    # firefly, t = firefly_algorithm(0, bmark=args.bmark, f=args.f, a=args.a, ca=args.ca, g=args.g, dlt=args.dlt, v=args.v, p=args.p, fname=args.fname, hdir=args.hdir, s=args.s, sch=args.sch)

    # firefly, t = firefly_algorithm(0, bmark=args.bmark, f=args.f, a=args.a, ca=args.ca, g=args.g, dlt=args.dlt, v=args.v, p=args.p, fname=args.fname, hdir=args.hdir, s=args.s, sch=args.sch)
    # while(True):
    #     # aparam = np.random.randint(1,8)
    #     # gparam = (0.001-0.00001)*np.random.rand()+0.00001
    #     # fparam = np.random.randint(40,80)
    #     # sparam = np.random.randint(10,150)
    #     dltparam = (1.0-0.1)*np.random.rand()+0.1
    #     caparam = np.random.randint(1,3)
    #     with open('{}'.format(args.fname), 'a') as f:
    #         # f.write('-a={}, -g={}, -f={}, -s={}\n'.format(aparam, gparam, fparam, sparam))
    #         f.write('-a={}, -g={}, -f={}, -dlt={}, -ca={}\n'.format(args.a, args.g, args.f, dltparam, caparam))
    #     # firefly, t = firefly_algorithm(0, bmark=args.bmark, f=fparam, a=aparam, ca=args.ca, g=gparam, dlt=dltparam, v=args.v, p=args.p, fname=args.fname, hdir=args.hdir, s=args.s, sch=args.sch)
    #     firefly, t = firefly_algorithm(0, bmark=args.bmark, f=args.f, a=args.a, ca=caparam, g=args.g, dlt=dltparam, v=args.v, p=args.p, fname=args.fname, hdir=args.hdir, s=args.s, sch=args.sch)
    # aparams = [3,5,8,10]
    # fnames = ['vrp/a2_paramtest/{}'.format(a) for a in aparams]
    # bmarks = ['Osaba_data/Osaba_50_1_1.xml', 'Osaba_data/Osaba_100_2.xml']
    # for bmark in bmarks:
    #     args.bmark=bmark
    #     for fname, a in zip(fnames, aparams):
    #         args.fname=fname + '_' + re.split('[/.]', bmark)[1].strip('Osaba_')
    #         args.a=a
    #         n_times_run(args)
    # while True:
    #     args.v=4
    #     all_bench_run(args)
    #     args.v=1
    #     all_bench_run(args)
    # all_bench_run(args)
    # bayes_estimation(args)
    # luminosities=[]
    # times=[]
    firefly, t = firefly_algorithm(0, bmark=args.bmark, f=args.f, a=args.a, ca=args.ca, g=args.g, dlt=args.dlt, v=args.v, p=args.p, fname=args.fname, hdir=args.hdir, s=args.s, sch=args.sch)
    # print(firefly.luminosity)
    # print(firefly.routes)
    #
    # with open('{}'.format(args.fname), 'a') as f:
    #     f.write("{}\n\n".format(firefly.routes))
    # print(customers)


    # print(coord)
    # a = [1,5,3,2,4,1,6,6,3,3,3,3,3,3]
    # b = [1,5,2,6,3,1,6,5,5,5,5,5,5,5]
    # print(beta_step(a,b,1,0.95,1))
