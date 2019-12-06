import matplotlib.pyplot as plt
import random

files = ['a5_linear_results', 'a5_sqrt_results']
data = []
for f in files:
    with open(f, 'r') as r:
        print(f)
        content = r.read().split('\n')[:-1]
    data.append([float(c)/10000 for c in content])
print(data)
names = ['alpha-step5-linear', 'alpha-step5-sqrt']
fig = plt.figure()
ax = fig.add_subplot(111)
boxplot = ax.boxplot(data)
for k in boxplot.keys():
    for b in boxplot[k]:
        b.set_linewidth(2)
ax.set_xticklabels(names)
# plt.xlabel('Method')
plt.ylabel('Best firefly')
plt.savefig('alphaboxplot.png', format='png', dpi=800, bbox_inches='tight')
