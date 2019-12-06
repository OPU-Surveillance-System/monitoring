import argparse
import copy
import matplotlib.pyplot as plt
import numpy as np
import os
import re
import seaborn as sns

def plot_alpha5_wins(parameter, alpha5_wins, **kwargs):
    param=[]
    wins=[]
    for i, p in enumerate(parameter):
        for j in alpha5_wins[i]:
            param.append(p)
            wins.append(j)
    plt.plot(param, wins, 'o')
    plt.xlabel(kwargs['p'])
    plt.ylabel('alpha5 wins')
    param_lim = {'a':[2,16], 'f':[10,50], 'g':[0.001,1], 'i':[100,1000], 's':[1,30]}
    plt.xlim(param_lim[kwargs['p']][0], param_lim[kwargs['p']][1])
    plt.ylim(0, 10)
    plt.savefig('hdi/random_parameters/random_parameters_plot/{}_plot.svg'.format(kwargs['p']), format='svg')
    plt.clf()

def draw_heatmap(parameter, alpha5_wins, **kwargs):
    param=[]
    wins=[]
    #区切り a=1, f=5, g=0.05, i=50, s=2ごと
    param_div = {'a':1, 'f':5, 'g':0.05, 'i':50, 's':2}
    div = param_div['{}'.format(kwargs['p'])]
    param_lim = {'a':[2,16], 'f':[10,50], 'g':[0.001,1], 'i':[100,1000], 's':[1,30]}
    lim = param_lim['{}'.format(kwargs['p'])]
    if kwargs['p'] == 'a' or kwargs['p'] == 's' or kwargs['p'] == 'g':
        param_wins_matrix=[[0 for j in range(int((lim[1]-lim[0])/div)+1)] for i in range(11)]
    else:
        param_wins_matrix=[[0 for j in range(int((lim[1]-lim[0])/div))] for i in range(11)]
    wins = each_param_win_mean(alpha5_wins)
    for i, p in enumerate(parameter):
        if p == lim[1] and (kwargs['p']=='f' or kwargs['p']=='i'):
            p-=1
        if kwargs['p'] == 'g':
            param_wins_matrix[10-wins[i]][int((p-lim[0])*1000/(div*1000))] += 1
        else:
            param_wins_matrix[10-wins[i]][int((p-lim[0])/div)] += 1
    ###rate
    rate_matrix = copy.deepcopy(param_wins_matrix)
    sum_each_param=[0 for i in range(len(rate_matrix[0]))]
    for wins_row in rate_matrix:
        for j, win in enumerate(wins_row):
            sum_each_param[j] += win
    for i in range(len(rate_matrix)):
        for j in range(len(rate_matrix[0])):
            rate_matrix[i][j] /= sum_each_param[j]
    ###
    fig=plt.figure(figsize=(12,9))
    sns.set(font_scale=1)
    data = np.array(rate_matrix)
    xlabels_set={'i':['{}-{}'.format(100+50*i, 149+50*i) for i in range(18)],
                'a':[2+i for i in range(15)],
                'f':['{}-{}'.format(10+5*i, 14+5*i) for i in range(8)],
                # 'g':['{}-{}'.format(100+50*i, 149+50*i) for i in range(18)]
                'g':['.001-.050','.050-.100','.100-.150','.150-.200','.200-.250','.250-.300','.300-.350','.350-.400','.400-.450','.450-.500','.500-.550','.550-.600','.600-.650','.650-.700','.700-.750','.750-.800','.800-.850','.850-.900','.900-.950','.950-1.000'],
                's':['{}-{}'.format(1+i*2, 2+i*2) for i in range(15)]}
    xlabels_set['i'][-1]='950-1000'
    xlabels_set['f'][-1]='45-50'

    xlabels=xlabels_set['{}'.format(kwargs['p'])]
    ylabels=[10-i for i in range(11)]

    fig = sns.heatmap(data, vmin=0, vmax=1, xticklabels=xlabels, yticklabels=ylabels, annot=True, fmt='.1g')
    fig.set(xlabel='iteration', ylabel='α2 < α5')
    plt.savefig('hdi/random_parameters/plot/{}_heatmap_rate'.format(kwargs['p']))

    # print(param_wins_matrix)
    # print(len(param_wins_matrix[0]))
    # print(data)


def fetch_parameter(**kwargs):
    path = 'hdi/random_parameters/exp/'
    param_folders = []
    param_num = []
    for param_folder in os.listdir(path):
        if os.path.isdir(path + param_folder):
            param_folders.append(param_folder)
    param_folders.sort(key=lambda x: int(re.search('[0-9]+', x).group()))
    for i in param_folders:
        with open('hdi/random_parameters/exp/{}/parameters'.format(i), 'r') as f:
            lines = f.readlines()
        params = lines[0].split(', ')
        for param in params:
            if re.match('-{}='.format(kwargs['p']), param):
                tmp = param.strip('-{}='.format(kwargs['p']))
                param_num.append(float(tmp))
    return param_num

def fetch_alpha5_wins_count():#try ファイル全読み
    path = 'hdi/random_parameters/exp/'
    param_folders = []
    param_num = []
    for folder in os.listdir(path):
        if os.path.isdir(path + folder):
            param_folders.append(folder)
    try_files = [[] for i in range(len(param_folders))]
    param_folders.sort(key=lambda x: int(re.search('[0-9]+', x).group()))
    for i, param_folder in enumerate(param_folders):
        for param_file in os.listdir(path+param_folder):
            if re.match('try', param_file):
                try_files[i].append(param_file)
    alpha5_wins = [[] for i in range(len(param_folders))]
    for i, param_folder in enumerate(param_folders):
        for try_file in try_files[i]:
            with open(path+param_folder+'/'+try_file, 'r') as f:
                lines = f.readlines()
            for line in lines:
                if re.match('alphaStep2 < alphaStep5 =', line):
                    alpha5_wins[i].append(int(line.split()[-1]))
    return alpha5_wins

def each_param_win_mean(alpha5_wins):
    round_int = lambda x: int((x*2+1)//2)
    wins = [0 for i in range(len(alpha5_wins))]
    for i, alpha5_win in enumerate(alpha5_wins):
        if len(alpha5_win) > 1:
            mean=[]
            for win in alpha5_win:
                mean.append(win)
            mean = np.mean(mean)
            mean = round_int(mean)
            wins[i] = mean
        else:
            wins[i] = alpha5_wins[i][0]
    return wins

def fetch_alpha5_hdi_wins():#各paramフォルダのhdi_resultによる
    path = 'hdi/random_parameters/exp/'
    param_folders = []
    param_num = []
    for folder in os.listdir(path):
        if os.path.isdir(path + folder):
            param_folders.append(folder)
    hdi_files = [[] for i in range(len(param_folders))]
    param_folders.sort(key=lambda x: int(re.search('[0-9]+', x).group()))
    for i, param_folder in enumerate(param_folders):
        for param_file in os.listdir(path+param_folder):
            if re.match('hdi_results', param_file):
                hdi_files[i].append(param_file)
    alpha5_wins = [[] for i in range(len(param_folders))]
    for i, param_folder in enumerate(param_folders):
        for hdi_file in hdi_files[i]:
            with open(path+param_folder+'/'+hdi_file, 'r') as f:
                lines = f.readlines()
            for line in lines:
                symbol = re.search('[<>=]', line).group()
                if symbol == '<':
                    alpha5_wins[i] = 1
                else:
                    alpha5_wins[i] = 0
    return alpha5_wins

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", type = str, default = 'a', help = "want paramter name")
    args = parser.parse_args()

    parameter = fetch_parameter(p=args.p)
    alpha5_wins = fetch_alpha5_wins_count()
    # alpha5_wins = fetch_alpha5_hdi_wins()
    draw_heatmap(parameter, alpha5_wins, p=args.p)
    # print(parameter.count(16))
    # with open('hdi/random_parameters/hdi_draw', 'w') as f:
    #     f.write('total: {}, α5_win: {}, draw: {}'.format(len(alpha5_wins), alpha5_wins.count(1), alpha5_wins.count(2)))



    # plot_alpha5_wins(parameter, alpha5_wins, p=args.p)
