"""
Define global variables for the overall system
"""

#Path variables
#TEMPLATE_PATH = "/home/scom/Documents/opu_surveillance_system/monitoring/master/"
#STATIC_PATH = "/home/scom/Documents/opu_surveillance_system/monitoring/static/"
TEMPLATE_PATH = "/home/jordan/Documents/tobikoma/monitoring/master/"
STATIC_PATH = "/home/jordan/Documents/tobikoma/monitoring/static"

#Map Converter
#X_SIZE = int(858 / 4)
#Y_SIZE = int(624 / 4)
#X_SIZE = 858
#Y_SIZE = 624
X_SIZE = 858 * 2 #One cell = 50cm
Y_SIZE = 624 * 2
ANGLE = 0.8447281091863906
REFERENCES = [[34.55016, 135.50109], [34.54064, 135.5123]]
RP_LATLON = [34.55016, 135.50613]
RP_UTM = (546436.7465413728, 3823275.6881677327, 53, 'S')

#Patrol planner
MAX_BATTERY_UNIT = 3000
