#Algo plus courts chemins pour drones

fi = 45
be = 0.2885
al = 3

it = 400000

# Reading
#with open("plots/bayesian/parameters", 'r') as f:
        #content = f.read()
#content.split('\n')[:-1]
#content = [[int(c[0]), float(c[1]), float(c[2])] for l in content for c l.split('\t')]

print("Firefly:", fi, " Beta:", be, " Alpha:", al)
 
import math

import random

import copy

import matplotlib.pyplot as plt

from sys import path

path.append("..")

path.append("../..")

import pickle
with open("../../webserver/data/serialization/mapper.pickle", "rb") as f:
        a = pickle.load(f)

import settings


a.paths[((528, 999), (528, 999))] = 0

# Constant for uncertainty
constant = 0.001279214

# Beta parameter (Gamma)
paramBeta = be

# Alpha parameter
paramAlpha = al

# Base: starting point and return point for all drones
O = 528, 999

# Checkpoints: points to visit
PointsList = [(32, 1122), (271, 1067), (209, 993), (184, 1205), (303, 1220), (400, 1122), (505, 1214), (669, 1202), (779, 1026), (912, 1029), (1483, 1156), (1614, 991), (1576, 567), (1502, 395), (1618, 227), (1448, 634), (967, 690), (1059, 842), (759, 823), (1387, 174), (1073, 82), (944, 327), (866, 512), (748, 638), (487, 896), (118, 653), (35, 902), (502, 339), (683, 316), (694, 123), (45, 52), (367, 39)]

# Initial solution (to be created)
Routes = []

# Another initial solution (already created)
Solution2 = [(1059, 842), (505, 1214), (400, 1122), (502, 339), (866, 512), (1073, 82), (669, 1202), (32, 1122), (45, 52), (209, 993), (118, 653), (487, 896), (748, 638), (271, 1067), (1576, 567), (683, 316), (1483, 1156), (1448, 634), (303, 1220), (759, 823), (1614, 991), (1387, 174), (1618, 227), (367, 39), (35, 902), (967, 690), (944, 327), (912, 1029), (184, 1205), (779, 1026), (694, 123), (1502, 395)]

# Maximum drone's energy (reloaded each time it reachs the base)
energyMax = 3000


Points = copy.deepcopy(PointsList)


# Distance between two points
def distance(x,y):
    r = a.paths[((x),(y))]
    if isinstance(r,int):
        return 0
    else:
        return r[1]


# FUNCTIONS FOR THE INITIAL SOLUTION:
# Shortest distance between a given point (x) and the other points (List)
def minDistance(x,List,indexs):
    j = indexs[0]
    m = distance(x,List[j])
    y = j
    for i in indexs:
        d = distance(x,List[i])
        if d < m:
            m = d
            y = i
    return m,y

# Find the points further from the origin (O) than a given point (x)
def furtherPoints(x,List):
    m = distance(x,O)
    indexs = []
    for i in range(0,len(List)):
        d = distance(O,List[i])
        d2 = distance(x,List[i])
        if((d >= m)&(d2 <= d)):
            indexs.append(i)
    return indexs

# Find the points located between the origin (O) and a given point (x)
def returnPoints(x,List):
    m = distance(x,O)
    indexs = []
    for i in range(0,len(List)):
        d = distance(O,List[i])
        d2 = distance(x,List[i])
        if((d <= m)&(d2 <= m)):
            indexs.append(i)
    return indexs

# Determine if it's possible to reach other points from the base (normally yes always)
def isPossible(List):
    r = True
    if len(List) > 0:
        m = minDistance(O,List,range(0,len(List)))
        if m[0] * 2 > energyMax:
            r = False
    else:
        r = False
    return r


# FUNCTIONS RELATED TO ROUTES:
# Return the cost of a path
def cost(List):
    #c = 0
    #for i in range(0,len(List)-1):
        #c = c + distance(List[i],List[i+1])
    l = [distance(List[i],List[i+1]) for i in range(0,len(List)-1)]
    return sum(l)

# Return the total cost of a list of paths
def costTotal(ListOfList):
    #c = 0
    #for List in ListOfList:
        #c = c + cost(List)
    l = [cost(List) for List in ListOfList]
    return sum(l)

# Return the total cost of several drones' paths
def costTotalMulti(Drones):
    #c = 0
    #for Drone in Drones:
        #c = c + costTotal(Drone)
    l = [costTotal(Drone) for Drone in Drones]
    return sum(l)


# Return the points' average uncertainty of a path
def uncertainty(List):
    dTot = cost(List)
    d = 0
    uTot = 0
    c = 0
    if len(List) == 0:
        return 0
    for i in range(0,len(List)-1):
        d = d + distance(List[i],List[i+1])
        if i > 0:
            c = c + 1
            t = (dTot - d)  / 2
            uTot = uTot + 1 - math.exp(-(constant * t))
    return (uTot / c)

# Return the points' average uncertainty of a list of paths
def uncertaintyTotal(ListOfList):
    dTot = costTotal(ListOfList)
    d = 0
    uTot = 0
    c = 0
    if len(ListOfList) == 0:
        return 0
    for List in ListOfList:
        for i in range(0,len(List)-1):
            d = d + distance(List[i],List[i+1])
            if i > 0:
                c = c + 1
                t = (dTot - d) / 2
                uTot = uTot + 1 - math.exp(-(constant * t))
    return (uTot / c)

# Return the points' average uncertainty of several drones' paths
def uncertaintyTotalMulti(Drones):
    #i = 0
    #for Drone in Drones:
        #i = i + uncertaintyTotal(Drone)
    l = [uncertaintyTotal(Drone) for Drone in Drones]
    return (sum(l) / len(Drones))


# Return the number of points in a list of paths
def length(ListOfList):
    #l = 0
    #for List in ListOfList:
        #l = l + len(List)
    l = [len(List) for List in ListOfList]
    return sum(l)


# FUNCTIONS FOR ROUTES' TRANSFORMATION:
# Merge two routes in one
def merge(Routes):
    routeComplete = []
    for Route in Routes:
        #l = len(Route)
        #for i in range(1,l-1):
            #routeComplete.append(Route[i])
        routeComplete = routeComplete + [Route[i] for i in range(1, len(Route)-1)]
    return routeComplete

# Merge routes of several drones
def mergeMulti(Drones):
    #routesCompletes = []
    #for Drone in Drones:
        #routesCompletes.append(merge(Drone))
    routesCompletes = [merge(Drone) for Drone in Drones]
    return routesCompletes

# Divide a road into different roads (based on energy)
def divide(Route):
    routeComplete = copy.deepcopy(Route)
    routes = []
    route = [O]
    e = energyMax
    while(len(routeComplete) > 0):
        last = route[len(route)-1]
        d = distance(last,routeComplete[0])
        if((e-d) >= distance(O,routeComplete[0])):
            e = e-d
            route.append(routeComplete[0])
            del routeComplete[0]
            if(len(routeComplete) == 0):
                route.append(O)
                routes.append(route)
        else:
            route.append(O)
            routes.append(route)
            route = [O]
            e = energyMax
    return routes

# Divide the roads of the drones in different roads
def divideMulti(Drones):
    #routes = []
    #for Drone in Drones:
        #routes.append(divide(Drone))
    routes = [divide(Drone) for Drone in Drones]
    return routes


# Swap the position of two values
def swap(List,swapIndexs):
    L = copy.deepcopy(List)
    v = L[swapIndexs[0]]
    L[swapIndexs[0]] = L[swapIndexs[1]]
    L[swapIndexs[1]] = v
    return L

# Swap the position of different couples of two values
def swapList(List,swapIndexsList):
    L = copy.deepcopy(List)
    for t in swapIndexsList:
        L = swap(L,t)
    return L

# Swap random values in the list
def randomSwap(List,n):
    L = copy.deepcopy(List)
    #indexs = []
    #for i in range(0,len(L)):
        #indexs.append(i)
    indexs = [i for i in range(0,len(L))]
    for j in range(0,n):
        if len(indexs) >= 2:
            x = random.choice(list(indexs))
            indexs.remove(x)
            y = random.choice(list(indexs))
            indexs.remove(y)
            L = swap(L,(x,y))
    return L

# Swap random values in the lists of several drones
def randomSwapMulti(Drones,n):
    #D = []
    #for Drone in Drones:
        #D.append(randomSwap(Drone,n))
    D = [randomSwap(Drone,n) for Drone in Drones]
    return D


# FUNCTIONS FOR FIREFLY:
# Hamming distance: number of elements placed differently from a list to an other
def hammingDistance(sol1, sol2):
    h = 0
    for i in range(0,len(sol1)):
        if sol1[i] != sol2[i]:
            h = h + 1
    return h

# Beta step: (exploitation)
def beta(sol1,sol2,n):
    sol = []
    h = hammingDistance(sol1,sol2)
    B = 1 / (1 + n * h)
    p = copy.deepcopy(PointsList)
    for i in range(0,len(sol1)):
        if sol1[i] == sol2[i]:      # If the two firefly as the same value at this place, then we keep it
            sol.append(sol1[i])
            p.remove(sol1[i])
        else:                # Otherwise, we accept the new one according to a certain % of probability
            r = random.randint(0,100) / 100
            if r < B:
                v = sol1[i]
            else:
                v = sol2[i]
            if v not in sol:
                sol.append(v)
                p.remove(v)
            else:                       # If the value is already in the new firefly, then we let a gap
                sol.append((0,0))
    for j in range(0,len(sol)):  # Finally, we add the remaining values in the gaps
        if sol[j] == (0,0):
            sol[j] = p[0]
            del p[0]
    return sol

# Alpha step : (exploration)
def alpha(solA,n):
    solB = copy.deepcopy(solA)
    indexs = []
    for i in range(0,len(solB)):
        indexs.append(i)
    while len(indexs) > n:                 # We remove elements in the list until we have only 'n' elements
        x = random.choice(list(indexs))
        indexs.remove(x)
    indexs2 = copy.deepcopy(indexs)
    random.shuffle(indexs2)            # And we mix these elements together
    while indexs2 == indexs:
        random.shuffle(indexs2) 
    for i in range(0,len(indexs)):
        solB[indexs[i]] = solA[indexs2[i]]
    return solB


# FUNCTIONS FOR ROAD DISTRIBUTION BETWEEN TWO DRONES:
# Fair distribution according to the number of points
def distribution1(Routes):
    R = copy.deepcopy(Routes)
    d1 = []
    d2 = []
    while len(R) > 0:
        L = list(map(len, R))
        i = L.index(max(L))
        if length(d1) <= length(d2):
            d1.append(R[i])
        else:
            d2.append(R[i])
        del R[i]
    return d1,d2

# Fair distribution according to the cost of paths
def distribution2(Routes):
    R = copy.deepcopy(Routes)
    d1 = []
    d2 = []
    while len(R) > 0:
        L = list(map(cost, R))
        i = L.index(max(L))
        if costTotal(d1) <= costTotal(d2):
            d1.append(R[i])
        else:
            d2.append(R[i])
        del R[i]
    return d1,d2

# Fair distribution according to the uncertainty of paths
def distribution3(Routes):
    R = copy.deepcopy(Routes)
    d1 = []
    d2 = []
    while len(R) > 0:
        L = list(map(uncertainty, R))
        i = L.index(max(L))
        if uncertaintyTotal(d1) <= uncertaintyTotal(d2):
            d1.append(R[i])
        else:
            d2.append(R[i])
        del R[i]
    return d1,d2

# Random distribution
def distributionRandom(Points):
    n = random.randint(1, len(Points)-2)
    d1 = []
    d2 = []
    for i in range(0,n+1):
        d1.append(Points[i])
    for j in range(n+1, len(Points)):
        d2.append(Points[j])
    return d1,d2


# FUNCTIONS FOR FIREFLY (Bis):
# Levenshtein distance: like Hamming distance, but also count the gaps
def levenshtein(L1,L2):
    l = min(len(L1),len(L2))
    lev = 0
    for i in range(0,l):
        if L1[i] != L2[i]:
            lev = lev + 1
    return lev + abs(len(L1) - len(L2))

# Beta step 2
def beta2(f1,f2,n):
    f = [[],[]]                # New firefly (firefly 2 attracted by firefly 1)
    lev = []                    # Levenshtein Distances
    p = copy.deepcopy(PointsList)
    f2bis = []
    c = 0
    #for i in range(0,len(f1)):         # Number of drones (2)
        #lev.append(levenshtein(f1[i],f2[i]))
        #for j in range(0,len(f2[i])):
            #f2bis.append(f2[i][j])
    lev = [levenshtein(f1[i],f2[i]) for i in range(0,len(f1))]
    f2bis = f2bis + [f2[i][j] for i in range(0,len(f1)) for j in range(0,len(f2[i]))]
    for i in range(0,len(f1)):
        B = 1 / (1 + n * lev[i])
        for j in range(0,len(f1[i])):
            if f1[i][j] == f2bis[c]:      # If the two firefly as the same value at this place, then we keep it
                f[i].append(f1[i][j])
                p.remove(f1[i][j])
            else:                   # Otherwise, we accept the new one according to a certain % of probability
                r = random.randint(0,100) / 100
                if r < B:
                    v = f1[i][j]
                else:
                    v = f2bis[c]
                if (v not in f[0]) & (v not in f[1]):
                    f[i].append(v)
                    p.remove(v)
                else:                       # If the value is already in the new firefly, then we let a gap
                    f[i].append((0,0))
            c = c + 1
    for i in range(0,len(f)):     # Finally, we add the remaining values in the gaps
        for j in range(0,len(f[i])):
            if f[i][j] == (0,0):
                f[i][j] = p[0]
                del p[0]
    return f

# Alpha step 2:
def alpha2(fA,n):
    fB = copy.deepcopy(fA)
    for i in range(0,len(fA)):
        #indexs = []
        #for j in range(0,len(fA[i])):
            #indexs.append(j)
        indexs = [j for j in range(0,len(fA[i]))]
        while len(indexs) > n:                 # We remove elements in the list until we have 'n' elements
            x = random.choice(list(indexs))
            indexs.remove(x)
        indexs2 = copy.deepcopy(indexs)
        random.shuffle(indexs2)            # And we mix these elements together
        while indexs2 == indexs:
            random.shuffle(indexs2)
        for j in range(0,len(indexs)):
            fB[i][indexs[j]] = fA[i][indexs2[j]]
    return fB

# Other step alpha idea (insert elements between drones)
def delta(fA,n):
    fB = copy.deepcopy(fA)
    for i in range(0,n):
        if((len(fB[0]) != 0) & (len(fB[1]) != 0)):
            d1 = random.randint(0,1)            # Drone who 'sends' an element
            d2 = random.randint(0,1)            # Drone who 'receives' an element
            n1 = random.randint(0,len(fB[d1])-1)            # index of the element to send
            n2 = random.randint(0,len(fB[d2])-1)            # index of the element to receive
            v = fB[d1][n1]
            del fB[d1][n1]
            fB[d2].insert(n2, v)
    return fB


def info(doubleRoutes):
    for n in range(0,2):
        c = costTotal(doubleRoutes[n])
        i = uncertaintyTotal(doubleRoutes[n])
        L = merge(doubleRoutes[n])
        print("Drone ",n+1)
        print("Length: ",len(L)," Cost: ",c," Uncertainty: ",i)



# Initial solution computation part:
Route = [O]
energy = energyMax
canContinue = isPossible(Points)
returnStep = False
# Main loop
while((len(Points) > 0) & canContinue):
    last = Route[len(Route)-1] # Last point of the current list
    indexs = furtherPoints(last,Points) # Indexs of the further points from the center
    if indexs == []: # If there is no further points, the drone returns to the base
        returnStep = True
    else: # Otherwise, we try to reach the nearest point among these further points
        n = minDistance(last,Points,indexs)
        if( (energy - n[0]) >= distance(O,Points[n[1]]) ): # If the drone has enough energy, he goes
            energy = energy - n[0]
            Route.append(Points[n[1]])
            del Points[n[1]] # In this case, we remove the point from the initial list (to not visit it again)
            if len(Points) == 0: # If it was the last point in the list, the drone returns to the base
                Route.append(O)
                Routes.append(Route)
        else: # If the drone hasn't enough energy to reach it and return to the base, then he directly returns to the base
            returnStep = True
    # Return to the base step
    if returnStep:
        indexs2 = returnPoints(last,Points)
        while(len(indexs2)>0): # While there is points on the return path
            n2 = minDistance(last,Points,indexs2)
            if( (energy - n2[0]) > distance(O,Points[n2[1]]) ): # We check if he can reach the nearest point on its path
                energy = energy - n2[0]
                Route.append(Points[n2[1]])
                del Points[n2[1]]
                indexs2 = returnPoints(last,Points) # We update the list of points of the return path
            else:
                indexs2 = []
        returnStep = False
        Route.append(O)
        Routes.append(Route)
        Route = [O]
        energy = energyMax
        canContinue = isPossible(Points) # We check if we can reach the remaining points

lasts = []
bests = []
bestPathEver = []

for m in range(0,1):
    Solutions = []
    
    # Recomputation of the initial firefly
    f = distribution1(Routes)
    f = mergeMulti(f)
    f = divideMulti(f)
    x = costTotalMulti(f)
    y = uncertaintyTotalMulti(f)
    f = mergeMulti(f)
    Solutions.append((f,x,y))

    # Fireflies creation based on initial firefly (random swaps)
    for i in range(0,fi-1):
        g = randomSwapMulti(f,3)
        g = divideMulti(g)
        x = costTotalMulti(g)
        y = uncertaintyTotalMulti(g)
        g = mergeMulti(g)
        Solutions.append((g,x,y))

    # Display of the starting fireflies
    for i in range(0, len(Solutions)):
        print("Cost: ", Solutions[i][1], ", Uncertainty: ", Solutions[i][2])


    # Firefly Part
    number = it
    last = Solutions[0][1]
    best = Solutions[0][1]
    bestIndex = 0
    bestOfTheBest = Solutions[0]
    counter = 0
    f3 = copy.deepcopy(PointsList)
    tab = ([0],[Solutions[0][1]],[Solutions[0][2]])
    print("Beta and Alpha steps (",number," fois)")
    
    # Loop done for each iteration
    for n in range(1,number+1):
        # Beta step
        for i in range(0, len(Solutions)-1):
            for j in range(i+1, len(Solutions)):
                if Solutions[i][1] != Solutions[j][1]:
                    if Solutions[i][1] < Solutions[j][1]:       # We looks which firefly is the 'best'
                        f1 = Solutions[i][0]
                        f2 = Solutions[j][0]
                        k = j
                    else:
                        f1 = Solutions[j][0]
                        f2 = Solutions[i][0]
                        k = i
                    g = beta2(f1,f2,paramBeta)                     # We run Beta step
                    g = divideMulti(g)
                    x = costTotalMulti(g)
                    y = uncertaintyTotalMulti(g)
                    g = mergeMulti(g)
                    Solutions[k] = (g,x,y)              # And we replace the 'worst' firefly by the new one

        # Best Firefly
        for i in range(0, len(Solutions)):
            if Solutions[i][1] < best:
                best = Solutions[i][1]
                bestIndex = i
        if best == last:                            # If the best firefly hasn't changed, then we increments the counter
            counter = counter + 1
        else:                                           # Otherwise, we reset it
            counter = 0
            last = best
            if best < bestOfTheBest[1]:
                bestOfTheBest = Solutions[bestIndex]
        if n % 100 == 0:
            print("Iteration: ", n)
            print("Best firefly:  cost: ", Solutions[bestIndex][1], ", uncertainty: ", Solutions[bestIndex][2])
            tab[0].append(n)
            tab[1].append(Solutions[bestIndex][1])
            tab[2].append(Solutions[bestIndex][2])

        # Etape Alpha 1 (original)
        for i in range(0, len(Solutions)):
            if (i != bestIndex): #| (counter > 1000):       # If the counter reachs 1000, the best firefly is unlocked
                g = alpha2(Solutions[i][0], paramAlpha)
                g = divideMulti(g)
                x = costTotalMulti(g)
                y = uncertaintyTotalMulti(g)
                g = mergeMulti(g)
                Solutions[i] = (g,x,y)
                #if (i == bestIndex):
                    #counter = 0
                    #best = Solutions[i][1]
                    #last = best

        # Alpha step 2 (using Beta step)
        #for i in range(0, len(Solutions)):
            #if (i != bestIndex): #| (counter > 1000): 
                #random.shuffle(f3)
                #f3bis = distributionRandom(f3)
                #g = beta2(f3bis,g,paramAlpha)
                #g = divideMulti(g)
                #x = costTotalMulti(g)
                #y = uncertaintyTotalMulti(g)
                #g = mergeMulti(g)
                #Solutions[i] = (g,x,y)
                #if (i == bestIndex):
                    #counter = 0
                    #best = Solutions[i][1]
                    #last = best

        # Alpha step 3 (elements insertion)
        #for i in range(0, len(Solutions)):
            #if (i != bestIndex): #| (counter > 1000): 
                #g = delta(Solutions[i][0],paramAlpha)
                #g = divideMulti(g)
                #x = costTotalMulti(g)
                #y = uncertaintyTotalMulti(g)
                #g = mergeMulti(g)
                #Solutions[i] = (g,x,y)
                #if (i == bestIndex):
                    #counter = 0
                    #best = Solutions[i][1]
                    #last = best

        # Display of the fireflies (every 1000 iterations)
        if n % 100 == 0:
            for i in range(0, len(Solutions)):
                print("Cost: ", Solutions[i][1], ", Uncertainty: ", Solutions[i][2])

    print("Best of the best firefly:  Cost: ", bestOfTheBest[1], ", Uncertainty: ", bestOfTheBest[2])

    best = True
    for i in range(0,len(bests)):
        if bestOfTheBest[1] > bests[i]:
            best = False
    if best:
        bestPathEver = bestOfTheBest[0]
    
    lasts.append(last)
    bests.append(bestOfTheBest[1])

    # Plot of the solutions' evolution
    plt.plot(tab[0],tab[1])
    plt.xlabel('Iterations')
    plt.ylabel('Best Firefly Cost')
    plt.savefig("plots/test.svg", format="svg")
    plt.show()
    #plt.clf()

print("List Lasts: ",lasts)
print("List Bests: ",bests)
print("Best path ever:",bestPathEver)
s = (sum(bests) / len(bests))
print("Average of bests:",s)


#return costTotalMulti(divideMulti(bestPathEver))

