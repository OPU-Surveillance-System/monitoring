#coding: utf-8
from matplotlib import pyplot as plt
import pandas as pd
import re
import numpy as np
import sys
from collections import OrderedDict
import scipy
import scipy.stats
import scipy.optimize
import pickle
import seaborn as sns

def plot_convergenceline():
    each_best=[[] for i in range(10)]
    for i in range(10):
        with open('vrp/exp_keep/nseg_i700dlt1/pickle/50_2_3-{}'.format(i), 'rb') as f:
            each_best[i] = pickle.load(f)
    each_best_mean=[0 for i in range(len(each_best[0]))]
    for i, ith_bests in enumerate(list(zip(*each_best))):
        each_best_mean[i] = np.mean(ith_bests)
    x=range(len(each_best_mean))
    y=each_best_mean
    plt.plot(x,y)
    plt.show()
    plt.clf()

def plot_segments():
    steps=[20,30,50,80,100,120,150]
    iteration=range(700)
    seg_maxsize = 10
    seg_f = lambda i,step : seg_maxsize - (i//step)
    for step in steps:
        segment = [2 if seg_f(t,step) < 2 else seg_f(t,step) for t in iteration]
        plt.plot(iteration, segment, label="s={}".format(step))
    plt.legend()
    plt.title("segments_transition")
    plt.xlabel("iteration")
    plt.ylabel("segment size")
    plt.savefig("vrp/importance/segments_transition.svg", format='svg')
    plt.clf()

# def plot_beta(a, b, bmark, update_num):#a, b: Beta distribution parameters
def plot_beta(a, b, update_num):#a, b: Beta distribution parameters
    """
    be used when u want to plot binomial distribution
    """
    x = np.linspace(0, 1, 100)
    plt.xlim(0, 1)
    plt.ylim(0, 5)
    # label
    rv = scipy.stats.beta(a, b)
    y = rv.pdf(x)
    plt.plot(x, y)
    plt.savefig("hdi/random_parameters/AROB_add_exp/{}.svg".format(update_num), format="svg")
    # plt.savefig("vrp/bayes_estimation/seg/d{}/{}.svg".format(bmark, try_count), format="svg")
    plt.clf()

def results2csv():
    # steps = ['80','100','120','150']
    steps = ['100']
    # dlts = ['0.76','0.90','1.00','3.00','5.00','10.00']
    probnames = ['50_1_1','50_1_2','50_1_3','50_1_4','50_2_1','50_2_2','50_2_3','50_2_4',
            '80_1','80_2','80_3','80_4','100_1','100_2','100_3']
    df = pd.DataFrame()
    # for step in steps:
    for step in steps:
        for probname in probnames:
            # with open('vrp/exp_seg/segrand/a=5/seg{}/{}'.format(step, probname)) as f:
            with open('vrp/exp_seg/segrand/a=8/seg{}/{}'.format(step, probname)) as f:
                for line in f:
                    if 'best:' in line:
                        s=pd.Series([float(re.split(' ',line)[1]),'%s'%step,'%s'%probname])
                        df=df.append(s, ignore_index=True)
    df.columns=['best', 'step', 'problem']
    df.to_csv('vrp/importance/a=8steps_data.csv')


def plot_lines_errorbar():

    df5=pd.read_csv('vrp/importance/a=5steps_data.csv')
    # df8=pd.read_csv('vrp/importance/a=8steps_data.csv')
    df=pd.read_csv('vrp/importance/dlts_data.csv')
    # print(df[df['problem']=='50_1_1'])
    # df1 = df[df['dlt']==0.76]
    # df1 = df1.append(df[df['dlt']==1.00])
    # df1 = df1.append(df[df['dlt']==10.00])
    df = df5[df5['step']==100]
    df.to_csv('vrp/importance/a=8steps_data.csv')
    # df=df.replace({100:'a=5_s=100'})
    # df = df.append(df8[df8['step']==100])
    # df=df.replace({100:'a=8_s=100'})
    # df = df.append(df8[df8['step']==120])
    # df=df.replace({120:'a=8_s=120'})

    fig = plt.figure()
    ax = fig.add_subplot()
    ax = sns.pointplot(x='problem', y='best', data=df1, hue='dlt', ci='sd', dodge=True)
    # ax = sns.violinplot(x='problem', y='best', data=df1, hue='dlt', split=True, inner='stick')

    plt.show()
    # plt.savefig('vrp/importance/steps.svg',format='svg')

def make_table():
    # columns = [['0.76','0.90','1.00','3.00','5.00','10.00'],['mean','std']]
    # columns = pd.MultiIndex.from_product(columns, names=['dlt',''])
    columns = [['20','30','50','80','100','120','150'],['mean','std']]
    columns = pd.MultiIndex.from_product(columns, names=['a=5 step',''])
    index = ['50_1_1(5)','50_1_2(5)','50_1_3(10)','50_1_4(10)','50_2_1(5)','50_2_2(5)','50_2_3(10)','50_2_4(10)',
            '80_1(8)','80_2(8)','80_3(10)','80_4(10)','100_1(10)','100_2(10)','100_3(10)']
    steps=sorted(list(columns.levels[0]), key=lambda c:float(c))
    mean_dic=OrderedDict()
    std_dic=OrderedDict()
    for step in steps:
        mean_dic['{}'.format(step)]=[]
        std_dic['{}'.format(step)]=[]
    probnames=[re.split('[()]',index[i])[0] for i in range(len(index))]
    for probname in probnames:
        for step in steps:
            with open('vrp/exp_seg/segrand/a=5/seg{}/{}'.format(step,probname)) as f:
                for line in f:
                    if 'mean:' in line:
                        mean_dic['{}'.format(step)].append(round(float(re.split(' ',line)[1]), 1))
                    elif 'std:' in line:
                        std_dic['{}'.format(step)].append(round(float(re.split(' ',line)[1]), 1))

    df=pd.DataFrame()
    for step in steps:
        df['m{}'.format(step)]=mean_dic['{}'.format(step)]
        df['s{}'.format(step)]=std_dic['{}'.format(step)]
    df.index=index
    df.index.name='problems(cluster)'
    df.columns=columns
    # print(df)
    names=['mean','std']
    for index_i in range(len(df)):
        prob='{}'.format(index[index_i])
        #means, stds: mean and std per index
        means=[]
        stds=[]
        for step in steps:
            means.append(df.loc[prob,(step,'mean')])
            stds.append(df.loc[prob,(step,'std')])
        stepmean=steps[np.argmin(means)]
        stepstd=steps[np.argmin(stds)]
        df.loc[prob,(stepmean,'mean')]='<font color="red"><b>'+str(df.loc[prob,(stepmean,'mean')])+'</b></font>'
        df.loc[prob,(stepstd,'std')]='<font color="blue"><b>'+str(df.loc[prob,(stepstd,'std')])+'</b></font>'
    df.to_html('pandtest.html', escape=False)

if __name__ == '__main__':
    # make_table()
    # plot_convergenceline()
    # plot_segments()
    # results2csv()
    plot_lines_errorbar()
