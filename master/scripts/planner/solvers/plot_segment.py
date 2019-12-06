import matplotlib.pyplot as plt

def displaySegment(segment):
    x = list(range(len(segment)))
    plt.plot(x, segment)
    plt.xlabel('')
    plt.ylabel('Segment size')
    plt.savefig("plots/segment.svg", format="svg")
    plt.clf()

# #s[[a-step,step,sch,iteration,experiment-iterations'Y/N']]
# s = [[4,59,'linear',1000,'N'], [4,95,'sqrt',1000,'N'], [5,24,'linear',1000,'N'], [4,21,'linear',774,'Y'], [4,62,'sqrt',1000,'Y'], [5,17,'linear',1000,'Y']]
# for i in s:
#     segment = list()
#     for j in range(i[3]):
#         if i[2] == "linear":
#             segment.append(32 - (j//i[1]))
#         elif i[2] == "sqrt":
#             segment.append(32 - (j**(1/2))//i[1])
#         if segment[-1] < 2:
#             segment[-1] = 2
#     x = list(range(len(segment)))
#     print(segment)
#     plt.plot(x, segment, label="alpha-step{}-{}-{}".format(i[0],i[2],i[4]))
# plt.legend()
# plt.savefig("plots/segments.svg", format="svg")

iteration = 1000
steps=[10, 20, 30, 50, 80, 100, 150, 200]

for s in steps:
    segment=[]
    for i in range(iteration):
        segment.append(10-(i//s))
        if segment[-1] < 2:
            segment[-1] = 2
    x = [i for i in range(iteration)]
    plt.plot(x, segment, label="step:{}".format(s))
plt.legend()
plt.savefig('vrp/segment_plot.svg', format='svg')
