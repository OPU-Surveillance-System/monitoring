import matplotlib.pyplot as plt
import random

files = ['results_alpha1', 'results_alpha2', 'results_alpha3', 'sim']
data = []
for f in files:
    with open(f, 'r') as r:
        print(f)
        content = r.read().split('\n')[:-1]
    data.append([float(c)/10000 for c in content])
print(data)
names = ['alpha-step1', 'alpha-step2', 'alpha-step3', 'simulated annealing']
fig = plt.figure()
ax = fig.add_subplot(111)
boxplot = ax.boxplot(data)
for k in boxplot.keys():
    for b in boxplot[k]:
        b.set_linewidth(2)
ax.set_xticklabels(names)
# plt.xlabel('Method')
plt.ylabel('Best firefly')
plt.savefig('alphaboxplot.eps', format='eps', dpi=800, bbox_inches='tight')
