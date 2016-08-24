import matplotlib.pyplot as plt
import operator

with open("memo_grid_search", "r") as f:
    data = f.read()
data = data.split("\n")[:-1]
data = [data[i].split(" ") for i in range(len(data))]
data = {(int(data[i][0]), float(data[i][1]), float(data[i][2])):float(data[i][3]) for i in range(len(data))}
sorted_data = sorted(data.items(), key=operator.itemgetter(1))
for i in range(10):
    print(sorted_data[i][0][0], sorted_data[i][0][1], sorted_data[i][0][2], sorted_data[i][1])
best_iteration = sorted_data[0][0][0]
best_tmax = sorted_data[0][0][1]
best_tmin = sorted_data[0][0][2]
iteration = [1000000, 900000, 800000, 700000, 500000, 400000, 300000, 200000, 100000, 90000, 80000, 70000, 50000, 40000, 30000, 20000, 10000, 9000, 8000, 7000, 6000, 5000, 4000, 3000, 2000, 1000, 500, 250, 100, 50, 25, 10]
tmax = [100000, 50000, 25000, 10000, 9000, 8000, 7000, 6000, 5000, 4000, 3000, 2000, 1000, 500, 250, 100]
tmin = [50, 40, 30, 20, 10, 5, 2, 1, 0.5, 0.25, 0.1, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01]
plot_iteration = []
for i in iteration:
    plot_iteration.append(data[(i, best_tmax, best_tmin)])
plot_tmax = []
for x in tmax:
    plot_tmax.append(data[(best_iteration, x, best_tmin)])
plot_tmin = []
for n in tmin:
    plot_tmin.append(data[(best_iteration, best_tmax, n)])
f, axarr = plt.subplots(3)
axarr[0].plot(iteration, plot_iteration)
axarr[0].set_title("Energy according to the number of iterations")
axarr[0].set_xlabel("number of iterations")
axarr[0].set_ylabel("energy")
axarr[1].plot(tmax, plot_tmax)
axarr[1].set_title("Energy according to the maximal temperature")
axarr[1].set_xlabel("maximal temperature")
axarr[1].set_ylabel("energy")
axarr[2].plot(tmin, plot_tmin)
axarr[2].set_title("Energy according to the minimal temperature")
axarr[2].set_xlabel("minimal temperature")
axarr[2].set_ylabel("energy")
plt.tight_layout()
plt.show()
