import matplotlib.pyplot as plt
import operator

with open("memo_min_uncertainty", "r") as f:
    data = f.read()
data = data.split("\n")[:-1]
data = [data[i].split(" ") for i in range(len(data))]
data = {(int(data[i][0]), float(data[i][1]), float(data[i][2])):float(data[i][3])  / 100 for i in range(len(data))}
sorted_data = sorted(data.items(), key=operator.itemgetter(1))
for i in range(10):
    print(sorted_data[i][0][0], sorted_data[i][0][1], sorted_data[i][0][2], sorted_data[i][1])
best_iteration = sorted_data[0][0][0]
best_tmax = sorted_data[0][0][1]
best_tmin = sorted_data[0][0][2]
iteration = [2000000, 1000000, 500000, 125000, 50000, 25000, 12500, 5000, 2500, 1250, 500, 250, 125, 50, 25, 12]
tmax = [5000, 2500, 1250, 750, 500, 250, 125, 100, 90, 80, 70, 60, 50, 40, 30, 20, 15]
tmin = [12, 10, 9, 8, 5, 4, 1, 0.9, 0.8, 0.5, 0.4, 0.1, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01]
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
axarr[0].plot(iteration, plot_iteration, c="r")
axarr[0].scatter(iteration, plot_iteration)
axarr[0].set_title("Energy according to the number of iterations")
axarr[0].set_xlabel("number of iterations")
axarr[0].set_ylabel("energy")
axarr[1].plot(tmax, plot_tmax, c="r")
axarr[1].scatter(tmax, plot_tmax)
axarr[1].set_title("Energy according to the maximal temperature")
axarr[1].set_xlabel("maximal temperature")
axarr[1].set_ylabel("energy")
axarr[2].plot(tmin, plot_tmin, c="r")
axarr[2].scatter(tmin, plot_tmin)
axarr[2].set_title("Energy according to the minimal temperature")
axarr[2].set_xlabel("minimal temperature")
axarr[2].set_ylabel("energy")
plt.tight_layout()
plt.show()
