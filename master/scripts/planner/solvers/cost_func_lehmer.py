from solver import Solver
import random
import math
import lehmer
import matplotlib.pyplot as plt
import pickle
from sys import path
path.append("..")
import map_converter as m

interval = [-1000, 1000]
fs = open("../../webserver/data/serialization/mapper.pickle", "rb")
mapper = pickle.load(fs)
fs.close()
base = [(1059, 842), (505, 1214), (400, 1122), (502, 339), (866, 512), (1073, 82), (669, 1202), (32, 1122), (45, 52), (209, 993), (118, 653), (487, 896), (748, 638), (271, 1067), (1576, 567), (683, 316), (1483, 1156), (1448, 634), (303, 1220), (759, 823), (1614, 991), (1387, 174), (1618, 227), (367, 39), (35, 902), (967, 690), (944, 327), (912, 1029), (184, 1205), (779, 1026), (694, 123), (1502, 395)]
a = [(i, sum([i[0]**2, i[1]**2])) for i in mapper.default_targets]
a = sorted(a, key=lambda x: x[1])
id_to_loc = {i+1:a[i][0] for i in range(len(a))}
loc_to_id = {a[i][0]:i+1 for i in range(len(a))}
alphabet = [i for i in range(1, len(a) + 1)]
fact = int(math.factorial(len(alphabet)))
#start = random.randint(0, fact)
start = [(209, 993), (32, 1122), (184, 1205), (303, 1220), (400, 1122), (1614, 991), (1483, 1156), (1059, 842), (912, 1029), (779, 1026), (967, 690), (1448, 634), (1576, 567), (1502, 395), (1618, 227), (1387, 174), (866, 512), (748, 638), (271, 1067), (35, 902), (118, 653), (45, 52), (367, 39), (502, 339), (505, 1214), (669, 1202), (759, 823), (944, 327), (1073, 82), (694, 123), (683, 316), (487, 896)]
start = [loc_to_id[i] for i in start]
start = lehmer.int_from_perm(alphabet, start)
cost = []
x = list()
plan = Solver(base, mapper, 1)
for i in range(start + interval[0], start + interval[1]):
    id_perm = lehmer.perm_from_int(alphabet, i)
    x.append(i - (start + interval[1]))
    state = [id_to_loc[j] for j in id_perm]
    plan.state = state
    cost.append(plan.compute_performance())
f, ax = plt.subplots()
ax.plot(x, cost, c="r")
ax.scatter(x, cost, c="b")
ax.set_xlabel("lehmer")
ax.set_ylabel("cost")
ax.set_title("Best at Lehmer " + str(start))
ax.set_xlim([x[0], x[len(x) - 1]])
plt.show()
