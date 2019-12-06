import argparse
import copy
import distance
import math
import numpy as np
import sys
import os
import time
import utm
import xml.etree.ElementTree as ET

def extract_xmldata(bmark):
    tree = ET.parse('{}'.format(bmark))
    root = tree.getroot()

    coordx = []
    coordy = []
    for x in root.iter('CoordX'):
        x = int(x.text)
        coordx.append(x)
    for y in root.iter('CoordY'):
        y = int(y.text)
        coordy.append(y)
    coord = [(x,y) for x,y in zip(coordx, coordy)]

    forbidden_i = []
    forbidden_j = []
    #forbidden_i to forbidden_j
    for i in root.iter('est1'):
        i = int(i.text)
        forbidden_i.append(i)
    for j in root.iter('est2'):
        j = int(j.text)
        forbidden_j.append(j)
    forbidden = [(i, j) for i, j in zip(forbidden_i, forbidden_j)]

    with open('vrp/coord5011utm.csv', 'w') as f:
        f.write("lat,long,name\n")
        for i in range(len(coord)):
            xy = utm.to_latlon(coord[i][0], coord[i][1], 30, 'U')
            f.write("{},{},{}\n".format(xy[0], xy[1], i))

    # with open('vrp/coord5011_.csv', 'r') as f:
    #     data = f.read()
    # lines = data.split('\n')
    # print(len(lines))
    # with open('vrp/coord5011a.csv', 'w') as f:
    #     f.write("lat,long,name\n")
    #     for i,line in enumerate(lines):
    #         f.write("{}{}\n".format(line, i))




extract_xmldata('Osaba_data/Osaba_50_1_1.xml')
