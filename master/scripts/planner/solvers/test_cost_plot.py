import matplotlib.pyplot as plt

with open("test_cost_res", "r") as f:
    data = f.read()
data = data.split("\n")[:-1]
data = [data[i].split(" ") for i in range(8, len(data))]
x = [int(data[i][0]) for i in range(len(data))]
cost = [float(data[i][1]) for i in range(len(data))]
time = [float(data[i][2]) for i in range(len(data))]
gain = [((cost[i-1] - cost[i])) / (time[i] - time[i - 1]) for i in range(1, len(data))]
gain = [gain[0]] + gain
print(cost, gain)
fig, ax1 = plt.subplots()
pcost, = ax1.plot(x, cost, color="r", label="cost")
ax1.scatter(x, cost, color="k")
ax1.axhline(9000, color="r", linestyle="--")
ax1.set_title("Cost evolution according to the number of iterations")
ax1.set_xlabel("iterations")
ax1.set_ylabel("cost")
ax2 = ax1.twinx()
pgain, = ax2.plot(x, gain, color="b", label="gain")
ax2.scatter(x, gain, color="k")
ax2.set_ylabel("gain")
ax2.axhline(0.99, color="b", linestyle="--")
plt.axvline(4000000, color="k",linestyle = ":")
plt.legend(handles=[pcost, pgain], loc=1)
plt.show()
