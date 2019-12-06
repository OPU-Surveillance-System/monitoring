import argparse
import copy
import distance
import math
import numpy as np
import re
import sys
import scipy
import scipy.stats
import scipy.optimize
import pymc3

from plot_kinds import plot_beta

class binomial():
    def __init__(self, a, b, confidence_mass):
        """
        hdi constructor:
            a, b: Initial Beta distribution parameters (float > 0)
            confidence_mass: Highest Density Interval (HDI)'s span (float 0 < x < 1)
        """
        self.a = a
        self.b = b
        self.confidence_mass = confidence_mass
        self.distrib = scipy.stats.beta(a, b)
        self.hdi = self.get_hdi()

    # def get_hdi(self):
    #     """
    #     Compute the Highest Density Interval of the team's distribution:
    #     Adapted from: https://stackoverflow.com/questions/22284502/highest-posterior-density-region-and-central-credible-region
    #     """
    #     inconfidence_mass = 1 - self.confidence_mass
    #
    #     def get_interval_width(low_tail):
    #         interval_width = self.distrib.ppf(self.confidence_mass + low_tail) - self.distrib.ppf(low_tail)
    #
    #         return interval_width
    #
    #     hdi_low_tail = scipy.optimize.fmin(get_interval_width, inconfidence_mass, ftol=1e-8, disp=False)[0]
    #     hdi = self.distrib.ppf([hdi_low_tail, self.confidence_mass + hdi_low_tail])
    #
    #     return hdi

    def get_hdi(self):
        return pymc3.stats.hpd(self.distrib.rvs(size=10000)).tolist()

    def update(self, n, z):
        """
        Update the Beta distribution:
            n: number of fireflyAlgorithm runs
            z: number of osaba > ours (ours is better than osaba)
        """
        self.a += z
        self.b += n - z
        self.distrib = scipy.stats.beta(self.a, self.b)
        self.hdi = self.get_hdi()

def bayes_estimation():
    """
    data extraction from "solvers/hdi/random_parameters_exp/"
    """
    path='/home/scom/Documents/monitoring/master/scripts/planner/solvers/hdi/random_parameters/'
    def win_count_per_batch(update_num, batch_size):
        seg_win = 0
        for i in range(batch_size):
            with open('{}exp/param{}/try0'.format(path, update_num*batch_size+i), 'r') as f:
                means=[float(re.split(' ', line)[1].strip('()mean:\n')) for line in f if 'mean' in line]
            if means[0] > means[1]:
                seg_win+=1
        return seg_win

    max_number_of_folders = 1000
    folders_idx = [i for i in range(max_number_of_folders)]
    np.random.shuffle(folders_idx)

    bayes_binomial = binomial(1, 1, 0.95)
    batch_size=10
    max_iter=max_number_of_folders//batch_size
    for i in range(max_iter):
        seg_win = win_count_per_batch(i, batch_size)
        bayes_binomial.update(batch_size, seg_win)
        plot_beta(bayes_binomial.a, bayes_binomial.b, i)
        if bayes_binomial.hdi[0] > 0.5:
            with open('{}/AROB_add_exp/result'.format(path), 'w') as f:
                f.write('win\n')
                f.write('hpd={}'.format(bayes_binomial.hdi))
                return
        elif bayes_binomial.hdi[1] <= 0.5:
            with open('{}/AROB_add_exp/result'.format(path), 'w') as f:
                f.write('lose')
                return
    with open('{}/AROB_add_exp/result'.format(path), 'w') as f:
        f.write('draw')

if __name__ == '__main__':
    bayes_estimation()
