from bmm150 import *
from micropyGPS import MicropyGPS
from time import *
from math import *
from lecture_compas_num import *
from utils import *
from lecture_gps_fct import *

print("strat")
############################INIT###############################
polygon_points = [
   (48.602725, -3.834250),
   (48.291210, -3.583421),
   (48.507350, -2.793577),
   (47.701964, -2.702852),
    (47.999214, -4.149120)]
#morlaix-carhaix-stBrieux-Vannes-Quimper
# polygon_points = [
#     (47.651057, -2.782935),
#     (47.649641, -2.782425),
#     (47.650642, -2.781626),
#     (47.651176, -2.781781)
# ]
compasNumerique = bmm150_I2C(sdaPin=2, sclPin=3)
uart = machine.UART(0, baudrate=9600, rx=machine.Pin(1), tx=machine.Pin(0))  # TX sur GPIO 1, RX sur GPIO 0
gps = MicropyGPS()

############################MAIN###############################
#position actuel
position = lecture_gps(gps, uart, satellite_bool)

#is_point_in_polygon = is_point_in_polygon(position[0], position[1], polygon_points):

#cap actuel
cap = int(lecture_cap(compasNumerique))
##########################TEST########################"
for i in range(20):
    position = lecture_gps(gps=gps, uart=uart, satellite_bool=1)
    cap = int(lecture_cap(compasNumerique))
    print("gsp", gps.valid)
    if gps.valid:
        point_in_polygon = is_point_in_polygon(position[0], position[1], polygon_points)
        print("le point est dans le polygon: ", point_in_polygon)
        
        if not point_in_polygon:
            closest = find_closest_point_polygon(position[0], position[1], polygon_points)
            # Calculer le cap pour retourner à l'intérieur
            bearing_to_polygon = int(calculate_cap(position[0], position[1], closest[0], closest[1]))
            print("Point le plus proche sur le polygone :", closest)
            print("Cap à suivre pour retourner au polygone :", bearing_to_polygon, "degrés")
        
    print("position", position[0], position[1])
    print("cap", cap)
    sleep_ms(2000)
    
    
    
