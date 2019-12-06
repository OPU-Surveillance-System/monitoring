import argparse
import copy
import cProfile
import distance
import math
import numpy as np
import sys
import os
import time
import xml.etree.ElementTree as ET
import vrp_firefly

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-bmark', type = str, default = "../Osaba_data/Osaba_50_1_1.xml", help = "benchmark xml_file name")
    parser.add_argument('-f', type = int, default = 100, help = "the number of firefly")
    parser.add_argument('-a', type = int, default = 1, help = "alpha step parameter")
    parser.add_argument('-g', type = float, default = 0.90, help = "insert customer rate")
    parser.add_argument('-dlt', type = float, default = 1.0, help = "insert cluster rate")
    parser.add_argument('-v', type = int, default = 1, help = "alpha step version")
    parser.add_argument('-p', type = int, default = 1, help = "vorbose information")
    parser.add_argument('-fname', type = str, default = 'testresult', help = "save file name")
    args = parser.parse_args()

    if os.path.exists('{}'.format(args.fname)):
        if vrp_firefly.confirm_input(args.fname):
            with open('{}'.format(args.fname), 'w') as f:
                print("clear previous text")

    # while(True):
    #     aparam = np.random.randint(1,5)
    #     gparam = (0.1-0.0001)*np.random.rand()+0.0001
    #     fparam = np.random.randint(20,100)
    #     with open('{}'.format(args.fname), 'a') as f:
    #         f.write('-a={}, -g={}, -f={}\n'.format(aparam, gparam, fparam))
    #     firefly = vrp_firefly._algorithm(bmark=args.bmark, f=fparam, a=aparam, g=gparam, dlt=args.dlt, p=args.p, fname=args.fname)
    # firefly = firefly_algorithm(bmark=args.bmark, f=args.f, a=args.a, g=args.g, dlt=args.dlt, p=args.p, fname=args.fname)
    # firefly = vrp_firefly.firefly_algorithm(vars(args))
    cProfile.run('vrp_firefly.firefly_algorithm(vars(args))', sort='time')

    # print(firefly.luminosity)
    # print(firefly.routes)
    #
    # with open('{}'.format(args.fname), 'a') as f:
    #     f.write("{}\n\n".format(firefly.routes))
