import matplotlib.pyplot as plt

with open("test_pen", "r") as f:
    data = f.read()
data = data.split("\n")[:-1]
data = [data[i].split(" ") for i in range(0, len(data))]
pen = [float(data[i][0]) for i in range(len(data))]
u = [float(data[i][1]) for i in range(len(data))]
d = [float(data[i][2]) for i in range(len(data))]
gain = [((d[i-1] - d[i])) / (u[i] - u[i - 1]) for i in range(1, len(data))]
gain = [gain[0]] + gain
print(u, d, gain)
fig, ax1 = plt.subplots()
pu, = ax1.plot(pen, u, color="r", label="uncertainty_rate")
ax1.scatter(pen, u, color="k")
#ax1.axhline(9000, color="r", linestyle="--")
ax1.set_title("Cost evolution according to the number of iterations")
ax1.set_xlabel("penalization coefficient")
ax1.set_ylabel("uncertainty rate")
ax2 = ax1.twinx()
pd, = ax2.plot(pen, d, color="b", linestyle="--", label="distance")
ax2.scatter(pen, d, color="k")
ax2.set_ylabel("distance")
#ax2.axhline(0.99, color="b", linestyle="--")
#plt.axvline(4000000, color="k",linestyle = ":")
plt.legend(handles=[pu, pd], loc=1)
plt.show()
