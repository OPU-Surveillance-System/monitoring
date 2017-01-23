import matplotlib.pyplot as plt

with open("test_cost_res_uncertaintybattery", "r") as f:
    data = f.read()
data = data.split("\n")[:-1]
data = [data[i].split(" ") for i in range(12, len(data))]
x = [int(data[i][0]) for i in range(len(data))]
cost = [float(data[i][1]) for i in range(len(data))]
time = [float(data[i][2]) for i in range(len(data))]
uncertainty = [float(data[i][3]) for i in range(len(data))]
distance = [float(data[i][4]) for i in range(len(data))]
gain = [((cost[i] - cost[i - 1])) / (time[i] - time[i - 1]) for i in range(1, len(data))]
gain = gain + [gain[len(gain) - 1]]
gain_u = [((uncertainty[i] - uncertainty[i - 1]) * 10000) / (time[i] - time[i - 1]) for i in range(1, len(data))]
gain_u = gain_u + [gain_u[len(gain_u) - 1]]
gain_d = [((distance[i] - distance[i - 1])) / (time[i] - time[i - 1]) for i in range(1, len(data))]
gain_d = gain_d + [gain_d[len(gain_d) - 1]]
#gain2 = [((cost[14] - cost[i])) / (time[i] - time[14]) for i in range(15, len(x))]
print("ITERATIONS", x)
print("COST", cost, gain)
print("UNCERTAINTY", uncertainty, gain_u)
print("DISTANCE", distance, gain_d)
#print(gain2)
fig, (x1, x2, x3) = plt.subplots(1, 3)
pcost, = x1.plot(x, cost, color="r", label="Cost")
x1.scatter(x, cost, color="k")
#ax1.axhline(9000, color="r", linestyle="--")
#axarr[0, 0].set_title("Cost evolution according to the number of iterations")
x1.set_xlabel("Iterations")
x1.set_ylabel("Cost")
ax2 = x1.twinx()
pgain, = ax2.plot(x, gain, color="b", label="Gain")
ax2.scatter(x, gain, color="k")
ax2.set_ylabel("Gain")
ax2.axhline(0.0, color="b", linestyle="--")
x1.axhline(7432, color="r", linestyle="--")
ax2.axvline(10000000, color="k",linestyle = ":")
plt.legend(handles=[pcost, pgain], loc=7)

pu, = x2.plot(x, uncertainty, color="r", label="Unc. r")
x2.scatter(x, uncertainty, color="k")
#ax1.axhline(9000, color="r", linestyle="--")
#axarr[1, 0].set_title("Cost evolution according to the number of iterations")
x2.set_xlabel("Iterations")
x2.set_ylabel("Uncertainty rate")
ax3 = x2.twinx()
pgainu, = ax3.plot(x, gain_u, color="b", label="Gain")
ax3.scatter(x, gain_u, color="k")
ax3.set_ylabel("Gain")
ax3.axhline(0.0, color="b", linestyle="--")
ax3.axvline(10000000, color="k",linestyle = ":")
plt.legend(handles=[pu, pgainu], loc=7)

pd, = x3.plot(x, distance, color="r", label="Dist")
x3.scatter(x, distance, color="k")
#ax1.axhline(9000, color="r", linestyle="--")
#axarr[2, 0].set_title("Cost evolution according to the number of iterations")
x3.set_xlabel("Iterations")
x3.set_ylabel("Distance")
ax4 = x3.twinx()
pgaind, = ax4.plot(x, gain_d, color="b", label="Gain")
ax4.scatter(x, gain_d, color="k")
ax4.set_ylabel("Gain")
ax4.axhline(0.0, color="b", linestyle="--")
ax4.axvline(10000000, color="k",linestyle = ":")
plt.legend(handles=[pd, pgaind], loc=7)
plt.show()


# f, axarr = plt.subplots(2, 2)
# axarr[0, 0].plot(x, y)
# axarr[0, 0].set_title('Axis [0,0]')
# axarr[0, 1].scatter(x, y)
# axarr[0, 1].set_title('Axis [0,1]')
# axarr[1, 0].plot(x, y ** 2)
# axarr[1, 0].set_title('Axis [1,0]')
# axarr[1, 1].scatter(x, y ** 2)
# axarr[1, 1].set_title('Axis [1,1]')
# # Fine-tune figure; hide x ticks for top plots and y ticks for right plots
# plt.setp([a.get_xticklabels() for a in axarr[0, :]], visible=False)
# plt.setp([a.get_yticklabels() for a in axarr[:, 1]], visible=False)
