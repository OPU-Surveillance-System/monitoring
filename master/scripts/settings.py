"""
Define global variables for the overall system
"""

import math

#Path variables
#TEMPLATE_PATH = "/home/scom/Documents/opu_surveillance_system/monitoring/master/"
#STATIC_PATH = "/home/scom/Documents/opu_surveillance_system/monitoring/static/"
TEMPLATE_PATH = "/home/jordan/Documents/tobikoma/monitoring/master/"
STATIC_PATH = "/home/jordan/Documents/tobikoma/monitoring/static"

#Map Converter
COEFF = 0.5
X_SIZE = int(858 / COEFF)
Y_SIZE = int(624 / COEFF)
#X_SIZE = 858
#Y_SIZE = 624
#X_SIZE = 858 * 2 #One cell = 50cm
#Y_SIZE = 624 * 2
ANGLE = 0.8447281091863906
REFERENCES = [[34.55016, 135.50109], [34.54064, 135.5123]]
RP_LATLON = [34.55016, 135.50613]
RP_UTM = (546436.7465413728, 3823275.6881677327, 53, 'S')
PARTICULAR_PROBA = 0.99
PARTICULAR_TIME = 3600 #seconds
LAMBDA = math.log(1 - PARTICULAR_PROBA) / PARTICULAR_TIME

#Patrol planner
SPEED = 1 #m/s
BATTERY_LIMIT = 25 #min
MAX_DISTANCE_AT_SPEED = BATTERY_LIMIT * SPEED * 60
MAX_BATTERY_UNIT = MAX_DISTANCE_AT_SPEED / COEFF
MAX_RANDOM_PLANNER_ITERATION = 100
TIMESTEP = 1 * COEFF #cell/seconds
