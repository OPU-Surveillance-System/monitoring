import matplotlib.pyplot as plt

with open("memo_lambda", "r") as f:
    data = f.read()
data = data.split("\n")[:-1]
data = [data[i].split(" ") for i in range(len(data))]
x = [data[i][0] for i in range(len(data))]
y = [data[i][1] for i in range(len(data))]
fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_title("Uncertainty grid's mean according to different values of lambda")
ax.set_xlabel("time (s)")
ax.set_ylabel("mean")
plt.show()
