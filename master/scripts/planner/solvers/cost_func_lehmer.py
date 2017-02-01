from solver import Solver
import random
import math
import lehmer
import matplotlib.pyplot as plt
import pickle
from sys import path
path.append("..")
import map_converter as m

fs = open("../../webserver/data/serialization/mapper.pickle", "rb")
mapper = pickle.load(fs)
fs.close()
base = [[(1059, 842), (505, 1214), (400, 1122), (502, 339), (866, 512), (1073, 82), (669, 1202), (32, 1122), (45, 52), (209, 993), (118, 653), (487, 896), (748, 638), (271, 1067), (1576, 567), (683, 316), (1483, 1156), (1448, 634), (303, 1220), (759, 823), (1614, 991), (1387, 174), (1618, 227), (367, 39), (35, 902), (967, 690), (944, 327), (912, 1029), (184, 1205), (779, 1026), (694, 123), (1502, 395)]]
a = [(i, sum([i[0]**2, i[1]**2])) for i in mapper.default_targets]
a = sorted(a, key=lambda x: x[1])
id_to_loc = {i+1:a[i][0] for i in range(len(a))}
alphabet = [i for i in range(1, len(a) + 1)]
fact = int(math.factorial(len(alphabet)))
start = random.randint(0, fact)
cost = []
x = range(start, start + 100)
xx = range(0, 100)
it = 0
plan = Solver(base, mapper, 1)
for i in x:
    id_perm = lehmer.perm_from_int(alphabet, i)
    state = [id_to_loc[i] for i in id_perm]
    plan.state = state
    cost.append(plan.compute_performance())
    print(i, cost[it])
    it += 1
f, ax = plt.subplots()
ax.plot(xx, cost, c="r")
ax.scatter(xx, cost, c="b")
ax.set_xlabel("lehmer")
ax.set_ylabel("cost")
plt.show()
