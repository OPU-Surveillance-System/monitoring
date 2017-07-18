#Algo plus courts chemins pour drones

def test(fi, be, al, it):
    fi = int(fi * 50)
    #be = be * 1
    al = int(al * 10)

    #Lecture
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

    # Constante pour calculer évolution incertitude
    constante = 0.001279214

    # Paramètre beta (en fait c'est plutot gamma):
    paramBeta = be

    # Paramètre alpha:
    paramAlpha = al

    # "Base": Point de départ et de retour des drones
    O = 528, 999

    # "Checkpoints": Points à visiter
    PointsListe = [(32, 1122), (271, 1067), (209, 993), (184, 1205), (303, 1220), (400, 1122), (505, 1214), (669, 1202), (779, 1026), (912, 1029), (1483, 1156), (1614, 991), (1576, 567), (1502, 395), (1618, 227), (1448, 634), (967, 690), (1059, 842), (759, 823), (1387, 174), (1073, 82), (944, 327), (866, 512), (748, 638), (487, 896), (118, 653), (35, 902), (502, 339), (683, 316), (694, 123), (45, 52), (367, 39)]

    # Liste de chemins de la solution initiale
    Routes = []

    # Solution de base
    Solution2 = [(1059, 842), (505, 1214), (400, 1122), (502, 339), (866, 512), (1073, 82), (669, 1202), (32, 1122), (45, 52), (209, 993), (118, 653), (487, 896), (748, 638), (271, 1067), (1576, 567), (683, 316), (1483, 1156), (1448, 634), (303, 1220), (759, 823), (1614, 991), (1387, 174), (1618, 227), (367, 39), (35, 902), (967, 690), (944, 327), (912, 1029), (184, 1205), (779, 1026), (694, 123), (1502, 395)]

    # Energie maximale du drone (rechargée à chaque retour à la base)
    energyMax = 3000


    # Copier liste
    def copieListe(Liste):
        L = []
        for i in range(0,len(Liste)):
            L.append(Liste[i])
        return L

    Points = copy.deepcopy(PointsListe)


    # Distance entre deux points
    def distance(x,y):
        r = a.paths[((x),(y))]
        if isinstance(r,int):
            return 0
        else:
            return r[1]


    # FONCTIONS DE CALCUL DE LA SOLUTION INITIALE:
    # Distance minimale entre un point donné (x) et les autres points (Liste)
    def minDistance(x,Liste,indexs):
        j = indexs[0]
        m = distance(x,Liste[j])
        y = j
        for i in indexs:
            d = distance(x,Liste[i])
            if d < m:
                m = d
                y = i
        return m,y

    # Calcul des points plus loin de l'origine qu'un point donné (x)
    def pointsPlusLoin(x,Liste):
        m = distance(x,O)
        indexs = []
        for i in range(0,len(Liste)):
            d = distance(O,Liste[i])
            d2 = distance(x,Liste[i])
            if((d >= m)&(d2 <= d)):
                indexs.append(i)
        return indexs

    # Calcul des points situés entre l'origine et un point donné (x)
    def pointsDeRetour(x,Liste):
        m = distance(x,O)
        indexs = []
        for i in range(0,len(Liste)):
            d = distance(O,Liste[i])
            d2 = distance(x,Liste[i])
            if((d <= m)&(d2 <= m)):
                indexs.append(i)
        return indexs

    # Calcule si il est possible de continuer à atteindre des points restants depuis la base (normalement oui toujours)
    def isPossible(Liste):
        r = True
        if len(Liste) > 0:
            m = minDistance(O,Liste,range(0,len(Liste)))
            if m[0] * 2 > energyMax:
                r = False
        else:
            r = False
        return r


    # FONCTIONS DE CALCUL LIéES AUX ROUTES
    # Calcule le cout d'un chemin
    def cout(Liste):
        c = 0
        for i in range(0,len(Liste)-1):
            c = c + distance(Liste[i],Liste[i+1])
        return c

    # Calcule le cout total d'une liste de chemins
    def coutTotal(ListeDeListe):
        c = 0
        for Liste in ListeDeListe:
            c = c + cout(Liste)
        return c

    # Calcul le cout total des chemins de plusieurs drones
    def coutTotalMulti(Drones):
        c = 0
        for Drone in Drones:
            c = c + coutTotal(Drone)
        return c

    # Calcule l'incertitude moyenne des points d'un chemin
    def incertitude(Liste):
        dTot = cout(Liste)
        d = 0
        uTot = 0
        c = 0
        if len(Liste) == 0:
            return 0
        for i in range(0,len(Liste)-1):
            d = d + distance(Liste[i],Liste[i+1])
            if i > 0:
                c = c + 1
                t = (dTot - d)  / 2
                uTot = uTot + 1 - math.exp(-(constante * t))
        return (uTot / c)

    # Calcule l'incertitude moyenne des points d'une liste de chemins
    def incertitudeTotale(ListeDeListe):
        dTot = coutTotal(ListeDeListe)
        d = 0
        uTot = 0
        c = 0
        if len(ListeDeListe) == 0:
            return 0
        for Liste in ListeDeListe:
            for i in range(0,len(Liste)-1):
                d = d + distance(Liste[i],Liste[i+1])
                if i > 0:
                    c = c + 1
                    t = (dTot - d) / 2
                    uTot = uTot + 1 - math.exp(-(constante * t))
        return (uTot / c)

    # Calcule l'incertitude moyenne des points des chemins de plusieurs drones
    def incertitudeTotaleMulti(Drones):
        i = 0
        for Drone in Drones:
            i = i + incertitudeTotale(Drone)
        return (i / len(Drones))


    # Calcule le nombre de points d'une liste de chemins:
    def longueur(ListeDeListe):
        l = 0
        for Liste in ListeDeListe:
            l = l + len(Liste)
        return l


    # FONCTIONS DE TRANSFORMATION DE ROUTES
    # Fusionne les routes en une seule
    def fusionner(Routes):
        routeComplete = []
        for Route in Routes:
            l = len(Route)
            for i in range(1,l-1):
                routeComplete.append(Route[i])
        return routeComplete

    # Fusionne les routes de plusieurs drones
    def fusionnerMulti(Drones):
        routesCompletes = []
        for Drone in Drones:
            routesCompletes.append(fusionner(Drone))
        return routesCompletes

    # Divise la route complète en plusieurs routes (en fonction de l'énergie)
    def diviser(Route):
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

    # Divise les routes complètes des drones en plusieurs routes
    def diviserMulti(Drones):
        routes = []
        for Drone in Drones:
            routes.append(diviser(Drone))
        return routes


    # Interchange la position de deux valeurs
    def swap(Liste,swapIndexs):
        L = copy.deepcopy(Liste)
        v = L[swapIndexs[0]]
        L[swapIndexs[0]] = L[swapIndexs[1]]
        L[swapIndexs[1]] = v
        return L

    # Interchange la position de plusieurs couples de deux valeurs
    def swapListe(Liste,swapIndexsListe):
        L = copy.deepcopy(Liste)
        for t in swapIndexsListe:
            L = swap(L,t)
        return L

    # Interchange des valeurs aléatoires dans la liste
    def randomSwap(Liste,n):
        L = copy.deepcopy(Liste)
        indexs = []
        for i in range(0,len(L)):
            indexs.append(i)
        for j in range(0,n):
            if len(indexs) >= 2:
                x = random.choice(list(indexs))
                indexs.remove(x)
                y = random.choice(list(indexs))
                indexs.remove(y)
                L = swap(L,(x,y))
        return L

    # Interchange des valeurs aléatoires dans les listes de plusieurs drones
    def randomSwapMulti(Drones,n):
        D = []
        for Drone in Drones:
            D.append(randomSwap(Drone,n))
        return D


    # FONCTIONS DE FIREFLY:
    # Distance de Hamming: (nombre d'éléments placés différemment d'une liste à une autre)
    def hammingDistance(sol1, sol2):
        h = 0
        for i in range(0,len(sol1)):
            if sol1[i] != sol2[i]:
                h = h + 1
        return h

    # Etape Beta: (exploitation)
    def beta(sol1,sol2,n):
        sol = []
        h = hammingDistance(sol1,sol2)
        B = 1 / (1 + n * h)
        p = copy.deepcopy(PointsListe)
        for i in range(0,len(sol1)):
            if sol1[i] == sol2[i]:      # Si les deux firefly ont la même valeur à un emplacement, on la garde
                sol.append(sol1[i])
                p.remove(sol1[i])
            else:                           # Sinon, on accepte la nouvelle selon un certain % de probabilité
                r = random.randint(0,100) / 100
                if r < B:
                    v = sol1[i]
                else:
                    v = sol2[i]
                if v not in sol:
                    sol.append(v)
                    p.remove(v)
                else:                       # Si la valeur est déjà dans la nouvelle firefly, on y laisse un vide
                    sol.append((0,0))
        for j in range(0,len(sol)): # Enfin, on ajoute les valeurs restantes dans les vides
            if sol[j] == (0,0):
                sol[j] = p[0]
                del p[0]
        return sol

    # Etape Alpha: (exploration)
    def alpha(solA,n):
        solB = copy.deepcopy(solA)
        indexs = []
        for i in range(0,len(solB)):
            indexs.append(i)
        while len(indexs) > n:      # On retire des éléments de la liste jusqu'à en avoir que 2 (par défaut)
            x = random.choice(list(indexs))
            indexs.remove(x)
        indexs2 = copy.deepcopy(indexs)
        random.shuffle(indexs2)            # Et on mélange ces éléments entre eux
        while indexs2 == indexs:            # (on s'assure de ne pas retomber sur le même ordre)
            random.shuffle(indexs2) 
        for i in range(0,len(indexs)):
            solB[indexs[i]] = solA[indexs2[i]]
        return solB


    # FONCTIONS DE DISTRIBUTION DE ROUTES POUR 2 DRONES:
    # Distribution équitable selon nombre de points
    def distribution1(Routes):
        R = copy.deepcopy(Routes)
        d1 = []
        d2 = []
        while len(R) > 0:
            L = list(map(len, R))
            i = L.index(max(L))
            if longueur(d1) <= longueur(d2):
                d1.append(R[i])
            else:
                d2.append(R[i])
            del R[i]
        return d1,d2

    # Distribution équitable selon coût des chemins
    def distribution2(Routes):
        R = copy.deepcopy(Routes)
        d1 = []
        d2 = []
        while len(R) > 0:
            L = list(map(cout, R))
            i = L.index(max(L))
            if coutTotal(d1) <= coutTotal(d2):
                d1.append(R[i])
            else:
                d2.append(R[i])
            del R[i]
        return d1,d2

    # Distribution équitable selon incertitude des chemins
    def distribution3(Routes):
        R = copy.deepcopy(Routes)
        d1 = []
        d2 = []
        while len(R) > 0:
            L = list(map(incertitude, R))
            i = L.index(max(L))
            if incertitudeTotale(d1) <= incertitudeTotale(d2):
                d1.append(R[i])
            else:
                d2.append(R[i])
            del R[i]
        return d1,d2

    # Distribution random
    def distributionRandom(Points):
        n = random.randint(1, len(Points)-2)
        d1 = []
        d2 = []
        for i in range(0,n+1):
            d1.append(Points[i])
        for j in range(n+1, len(Points)):
            d2.append(Points[j])
        return d1,d2


    # FONCTIONS DE FIREFLY (Bis):
    # Distance de Levenshtein (comme distance de Hamming, mais compte aussi les vides):
    def levenshtein(L1,L2):
        l = min(len(L1),len(L2))
        lev = 0
        for i in range(0,l):
            if L1[i] != L2[i]:
                lev = lev + 1
        return lev + abs(len(L1) - len(L2))

    # Etape Beta 2
    def beta2(f1,f2,n):
        f = [[],[]]               # Nouvelle firefly 2 -> 1
        lev = []                    # Distances de Levenshtein
        p = copy.deepcopy(PointsListe)
        f2bis = []
        c = 0
        #for i in range(0,len(f1)):         # Nombre de drones (2)
            #lev.append(levenshtein(f1[i],f2[i]))
            #for j in range(0,len(f2[i])):
                #f2bis.append(f2[i][j])
        lev = [levenshtein(f1[i],f2[i]) for i in range(0,len(f1))]
        for i in range(0,len(f1)):
            f2bis = f2bis + [f2[i][j] for j in range(0,len(f2[i]))]
        for i in range(0,len(f1)):
            B = 1 / (1 + n * lev[i])
            for j in range(0,len(f1[i])):
                if f1[i][j] == f2bis[c]:      # Si les deux firefly ont la même valeur à un emplacement, on la garde
                    f[i].append(f1[i][j])
                    p.remove(f1[i][j])
                else:                           # Sinon, on accepte la nouvelle selon un certain % de probabilité
                    r = random.randint(0,100) / 100
                    if r < B:
                        v = f1[i][j]
                    else:
                        v = f2bis[c]
                    if (v not in f[0]) & (v not in f[1]):
                        f[i].append(v)
                        p.remove(v)
                    else:                       # Si la valeur est déjà dans la nouvelle firefly, on y laisse un vide
                        f[i].append((0,0))
                c = c + 1
        for i in range(0,len(f)):     # Enfin, on ajoute les valeurs restantes dans les vides
            for j in range(0,len(f[i])):
                if f[i][j] == (0,0):
                    f[i][j] = p[0]
                    del p[0]
        return f

    # Etape Alpha 2
    def alpha2(fA,n):
        fB = copy.deepcopy(fA)
        for i in range(0,len(fA)):
            #indexs = []
            #for j in range(0,len(fA[i])):
                #indexs.append(j)
            indexs = [j for j in range(0,len(fA[i]))]
            while len(indexs) > n:      # On retire des éléments de la liste jusqu'à en avoir que 'n'
                x = random.choice(list(indexs))
                indexs.remove(x)
            indexs2 = copy.deepcopy(indexs)
            random.shuffle(indexs2)            # Et on mélange ces éléments entre eux
            while indexs2 == indexs:            # (on s'assure de ne pas retomber sur le même ordre)
                random.shuffle(indexs2)
            for j in range(0,len(indexs)):
                fB[i][indexs[j]] = fA[i][indexs2[j]]
        return fB

    # Autre idée d'étape alpha (insertions d'éléments entre les drones)
    def delta(fA,n):
        fB = copy.deepcopy(fA)
        for i in range(0,n):
            if((len(fB[0]) != 0) & (len(fB[1]) != 0)):
                d1 = random.randint(0,1)            # drone qui 'envoie' un élément
                d2 = random.randint(0,1)            # drone qui 'reçoit' un élément
                n1 = random.randint(0,len(fA[d1])-1)            # index de l'élément à envoyer
                n2 = random.randint(0,len(fA[d2])-1)            # index de l'élement à recevoir
                print("d1:",d1,"d2:",d2,"n1:",n1,"n2:",n2)
                v = fB[d1][n1]
                del fB[d1][n1]
                fB[d2].insert(n2, v)
        return fB


    def info(doubleRoutes):
        for n in range(0,2):
            c = coutTotal(doubleRoutes[n])
            i = incertitudeTotale(doubleRoutes[n])
            L = fusionner(doubleRoutes[n])
            print("Drone ",n+1)
            print("Longueur: ",len(L)," Cout: ",c," Incertitude: ",i)



    # Partie calcul de la solution initiale
    Route = [O]
    energy = energyMax
    continuer = isPossible(Points)
    retour = False
    # Boucle principale
    while((len(Points) > 0) & continuer):
        last = Route[len(Route)-1] # Point de référence: dernier point de la liste actuelle
        indexs = pointsPlusLoin(last,Points) # Indexs des points situés plus loin du centre
        if indexs == []: # Si il n'y a aucun point situé plus loin, on retourne à la base
            retour = True
        else: # Sinon, on cherche à rejoindre le point le plus proche parmi ces 'points plus loin'
            n = minDistance(last,Points,indexs)
            if( (energy - n[0]) >= distance(O,Points[n[1]]) ): # Si le drone a assez d'énergie, il y va
                energy = energy - n[0]
                Route.append(Points[n[1]])
                del Points[n[1]] # Dans ce cas, on retire le plus de la liste initiale (car déjà visité)
                if len(Points) == 0: # Si il s'agissait du dernier point de la liste, on retourne à la base
                    Route.append(O)
                    Routes.append(Route)
            else: # Si le drone n'a pas assez d'énergie pour y aller puis retourner à la base, il y retourne
                retour = True
        # Phase de retour à la base:
        if retour:
            indexs2 = pointsDeRetour(last,Points)
            while(len(indexs2)>0): # Tant qu'il y a des points sur le retour
                n2 = minDistance(last,Points,indexs2)
                if( (energy - n2[0]) > distance(O,Points[n2[1]]) ): # On regarde s'il peut atteindre le plus proche
                    energy = energy - n2[0]
                    Route.append(Points[n2[1]])
                    del Points[n2[1]]
                    indexs2 = pointsDeRetour(last,Points) # On met à jour la liste des points sur le retour
                else:
                    indexs2 = []
            retour = False
            Route.append(O)
            Routes.append(Route)
            Route = [O]
            energy = energyMax
            continuer = isPossible(Points) # On regarde si les points restants sont atteignables (normalement oui)

    #lasts = []
    bests = []
    #bestCheminEver = []

    for m in range(0,10):
        Solutions = []
        
        # Re-calcul de la firefly initiale
        f = distribution1(Routes)
        f = fusionnerMulti(f)
        f = diviserMulti(f)
        x = coutTotalMulti(f)
        y = incertitudeTotaleMulti(f)
        f = fusionnerMulti(f)
        Solutions.append((f,x,y))

        # Création de firefly à partir de la firefly initiale
        for i in range(0,fi-1):
            g = randomSwapMulti(f,3)
            g = diviserMulti(g)
            x = coutTotalMulti(g)
            y = incertitudeTotaleMulti(g)
            g = fusionnerMulti(g)
            Solutions.append((g,x,y))

        # Affichage des firefly de départ
        #for i in range(0, len(Solutions)):
            #print("Cout: ", Solutions[i][1], ", Incertitude: ", Solutions[i][2])


        # Partie Firefly
        nombre = it
        last = Solutions[0][1]
        best = Solutions[0][1]
        bestIndex = 0
        bestOfTheBest = Solutions[0]
        compteur = 0
        f3 = copy.deepcopy(PointsListe)
        #tab = ([0],[Solutions[0][1]],[Solutions[0][2]])
        #print("Etapes Beta et Alpha (",nombre," fois)")
        
        # Boucle effectuée pour chaque itération
        for n in range(1,nombre+1):
            # Etape Beta
            for i in range(0, len(Solutions)-1):
                for j in range(i+1, len(Solutions)):
                    if Solutions[i][1] != Solutions[j][1]:
                        if Solutions[i][1] < Solutions[j][1]:       # On regarde quelle est la 'meilleure' firefly des deux
                            f1 = Solutions[i][0]
                            f2 = Solutions[j][0]
                            k = j
                        else:
                            f1 = Solutions[j][0]
                            f2 = Solutions[i][0]
                            k = i
                        g = beta2(f1,f2,paramBeta)                     # On applique l'étape Beta
                        g = diviserMulti(g)
                        x = coutTotalMulti(g)
                        y = incertitudeTotaleMulti(g)
                        g = fusionnerMulti(g)
                        Solutions[k] = (g,x,y)              # Et on remplace donc la plus 'mauvaise' par la nouvelle créée

            # Best Firefly
            for i in range(0, len(Solutions)):
                if Solutions[i][1] < best:
                    best = Solutions[i][1]
                    bestIndex = i
            if best == last:                            # Si la meilleure firefly n'a pas changé, on incrémente le compteur
                compteur = compteur + 1
            else:                                           # Sinon, on le réinitialise
                compteur = 0
                last = best
                if best < bestOfTheBest[1]:
                    bestOfTheBest = Solutions[bestIndex]
            #if n % 100 == 0:
                #print("Iteration: ", n)
                #print("Best firefly:  Cout: ", Solutions[bestIndex][1], ", Incertitude: ", Solutions[bestIndex][2])
                #tab[0].append(n)
                #tab[1].append(Solutions[bestIndex][1])
                #tab[2].append(Solutions[bestIndex][2])

            # Etape Alpha du prof (qui utilise la fonction Beta)
            #for i in range(0, len(Solutions)):
                #if (i != bestIndex): #| (compteur > 1000): 
                    #random.shuffle(f3)
                    #f3bis = distributionRandom(f3)
                    #g = beta2(f3bis,g,paramAlpha)
                    #g = diviserMulti(g)
                    #x = coutTotalMulti(g)
                    #y = incertitudeTotaleMulti(g)
                    #g = fusionnerMulti(g)
                    #Solutions[i] = (g,x,y)
                    #if (i == bestIndex):
                        #compteur = 0
                        #best = Solutions[i][1]
                        #last = best

            # Autre étape Alpha (insertions éléments)
            for i in range(0, len(Solutions)):
                if (i != bestIndex): #| (compteur > 1000): 
                    g = delta(Solutions[i][0],paramAlpha)
                    g = diviserMulti(g)
                    x = coutTotalMulti(g)
                    y = incertitudeTotaleMulti(g)
                    g = fusionnerMulti(g)
                    Solutions[i] = (g,x,y)
                    #if (i == bestIndex):
                        #compteur = 0
                        #best = Solutions[i][1]
                        #last = best
            
            # Etape Alpha
            #for i in range(0, len(Solutions)):
                #if (i != bestIndex): #| (compteur > 1000):       # Si le compteur a dépassé 1000, la meilleure se débloque
                    #g = alpha2(Solutions[i][0], paramAlpha)
                    #g = diviserMulti(g)
                    #x = coutTotalMulti(g)
                    #y = incertitudeTotaleMulti(g)
                    #g = fusionnerMulti(g)
                    #Solutions[i] = (g,x,y)
                    #if (i == bestIndex):
                        #compteur = 0
                        #best = Solutions[i][1]
                        #last = best
            
            # Affichage des Firefly (toutes les 1000 itérations)
            #if n % 1000 == 0:
                #for i in range(0, len(Solutions)):
                    #print("Cout: ", Solutions[i][1], ", Incertitude: ", Solutions[i][2])

        #print("Best of the best firefly:  Cout: ", bestOfTheBest[1], ", Incertitude: ", bestOfTheBest[2])

        #meilleur = True
        #for i in range(0,len(bests)):
            #if bestOfTheBest[1] > bests[i]:
                #meilleur = False
        #if meilleur:
            #bestCheminEver = bestOfTheBest[0]
        
        #lasts.append(last)
        bests.append(bestOfTheBest[1])

        # Graphique de l'évolution des solutions
        #plt.plot(tab[0],tab[1])
        #plt.xlabel('Iterations')
        #plt.ylabel('Best Firefly Cost')
        #plt.savefig("plots/%d.svg"%(numero), format="svg")
        #plt.show()
        #plt.clf()

    #print("Liste Lasts: ",lasts)
    #print("Liste Bests: ",bests)
    #print("Best chemin ever:",bestCheminEver)
    s = (sum(bests) / len(bests))
    print("Moyenne Bests:",s)

    #Ecriture
    with open("plots/bayesian/parameters", 'a') as f:
        line = '%d\t%.4f\t%.4f\t%f\n'%(fi, be, al, s)
        f.write(line)

    #return coutTotalMulti(diviserMulti(bestCheminEver))
    return s


# Partie Optimisation Bayesienne:
import GPy
import GPyOpt
from numpy.random import seed

def myf(x):
    #print("firefly: ", x[:,0], "beta: ", x[:,1], "alpha:", x[:,2])
    t = test(x[:,0],x[:,1],x[:,2],100000)
    return t

bounds = [{'name': 'var_1', 'type': 'continuous',  'domain': (0.2,1)},       # Firefly
                {'name': 'var_2', 'type': 'continuous',  'domain': (0,1)},           # Beta (Gamma)
                {'name': 'var_3', 'type': 'continuous', 'domain': (0.1,1)}]          # Alpha

n_iter = 100
max_iter = 1

xOpt =[]
fxOpt = []

# stores the problem
#seed(123)
#myProblem = GPyOpt.methods.BayesianOptimization(myf,bounds, acquisition_type='EI',exact_feval = True)
myProblem = GPyOpt.methods.BayesianOptimization(myf,bounds,batch_size=6,num_cores=6,evaluator_type="random")

for i in range(0,n_iter):
    # run the optimization for the given number of iterations
    myProblem.run_optimization(max_iter)

    # best found location
    #print(myProblem.x_opt)
    x = myProblem.x_opt
    x[0] = int(x[0] * 50)
    x[1] = x[1] * 1
    x[2] = x[2] * 10
    xOpt.append(x)

    # predicted value of f(x)
    #print(myProblem.fx_opt)
    fxOpt.append(myProblem.fx_opt)

    # result of the optimization
    #myProblem.plot_acquisition()

    myProblem.plot_convergence(filename="plots/bayesian/plot%dbayes.png"%(i+1))

k = fxOpt.index(min(fxOpt))
print("best x: ", xOpt[k])
print("best fx: ", fxOpt[k])
