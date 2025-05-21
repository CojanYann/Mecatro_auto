from machine import Pin, ADC, time_pulse_us
import utime
#from test import lecture_det_metaux
from mouvements import *
from lecture_ultrason import *
from depart_ok import depart_ok
import machine
import time

# Définition des pins
METAL_DETECTOR_PIN = 26  # Pin pour le détecteur de métaux
# Autres pins (moteurs, etc.)

# Variable pour suivre l'état de détection
metal_detected = False

# Fonction de callback pour l'interruption
def metal_detection_callback(pin):
    global metal_detected
    metal_detected = True
    print("Métal détecté!")

# Configuration de l'interruption pour le détecteur de métaux
detector_pin = machine.Pin(METAL_DETECTOR_PIN, machine.Pin.IN)
detector_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=metal_detection_callback)
#detector_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=metal_detection_callback)


# Fonction pour le cycle de ramassage
def collect_metal():
    print("Démarrage du cycle de ramassage")
    # Code pour activer les moteurs, ramasser le métal, etc.
    av()
    sleep(3)
    stop()
    time.sleep(1)  # Simulation du temps de ramassage
    print("Fin du cycle de ramassage")
    
# Boucle principale
def main():
    global metal_detected
    
    print("Démarrage du robot ramasseur de déchets")
    
    try:
    
        while True:
            # Si un métal a été détecté par l'interruption
            if metal_detected:
                collect_metal()
                metal_detected = False  # Réinitialiser l'état
            # Autres tâches du robot (déplacement, etc.)
            time.sleep(0.1)  # Petit délai pour éviter de surcharger le CPU
            dist = mesure_distance()
            
            # Gestion des obstacles
            if dist < 5:
                print(f"Obstacle proche: {dist:.1f} cm")
                stop()
                sleep(1)
                arr()  # Recule
                sleep(1)
                stop()
            
            # Condition d'arrêt
            if dist < 1:
                print("Obstacle trop proche, arrêt du programme")
                stop()
                break
            else:
                print(dist)
            
            # Déplacement normal
            av()
            sleep(0.5)
            stop()
            sleep(0.1) 
        
    except KeyboardInterrupt:
        print("Programme arrêté par l'utilisateur")
    finally:
        stop()
        print("Moteurs arrêtés")

main()
    
# from micropyGPS import MicropyGPS
# from bmm150 import *
# from lcd_api import LcdApi
# from pico_i2c_lcd import I2cLcd
# 
# from time import *
# from math import *
# from utime import sleep
# from machine import Pin, PWM
# 
# sleep(1)  # Laissez les capteurs s'initialiser
# 
# from lecture_compas_num import *
# from lecture_detecteur_met import *
# from lecture_gps_fct import *



# from lecture_lcd import *
# #from mouvements import *
# from utils import *
# from mouvements import *
# from lecture_ultrason import *
# from lecture_detecteur_met import *
# 
# vitesse(60000)
# while True:
#     met = lecture_det_metaux()
#     dist = mesure_distance(trig=15, echo=14)
#     print(met)
#     if met:
#         print("metal!!!!")
#         stop()
#         sleep(2)
#     if dist < 5 :
#         print("dis: ", dist)
#         stop()
#         sleep(1)
#         arr()
#         stop()
#     if dist <1:
#         stop()
#         break
#     stop()
#     sleep(0.15)
# stop()
      

##########################################GPS#####################################
# print("start")
# uart, gps, satellite_bool = init_gps()
# 
# lcd = init_lcd()
# 
# polygon_in = [
#     (47.650873, -2.783410),
#     (47.649930, -2.783383),
#     (47.650364, -2.781688),
#     (47.650892, -2.782289)
# ]
# 
# polygon_out = [
#     (47.650913, -2.782998),
#     (47.651112, -2.782009),
#     (47.651327, -2.783151),
#     (47.651469, -2.782360)
#     ]
# 
# for i in range(20):
#     lcd.clear()
#     print("lecture")
#     coord = lecture_gps(gps, uart, satellite_bool)
#     if "GPS" not in coord:
#         coord_str_lat = str(coord[0])
#         coord_str_lon = str(coord[1])
#         lat = float(coord[0])
#         lon = float(coord[1])
#         print("lat ", lat, " lon ", lon)
#         lcd.move_to(0,0)
#         lcd.putstr(coord_str_lat)
#         lcd.move_to(0,1)
#         lcd.putstr(coord_str_lon)
#         inside = is_point_in_polygon(lat, lon, polygon_out)
#         sleep(1)
#         
#         if inside:
#             lcd.move_to(0,1)
#             lcd.putstr("Dedans")
#         else:
#             lcd.move_to(0,1)
#             lcd.putstr("Retour en zone")
#             sleep(1)
#             clos_pt = find_closest_point_polygon(lat, lon, polygon_out)
#             print("point retour: ", clos_pt)
#             cap_retour = calculate_cap(lat, lon, clos_pt[0], clos_pt[1])
#             lcd.clear()
#             lcd.move_to(0,1)
#             lcd.putstr(str(cap_retour))
#         
#     else:
#         print("lat ", coord)
#         lcd.move_to(0,0)
#         lcd.putstr(coord)
#         print("recherche satellite ...")
#         i=0
#         while ("GPS" in coord) and i<=60:
#             coord = lecture_gps(gps, uart, satellite_bool)
#             i += 1
#             sleep(1)
#         print("fin de recherche")
#         
#     utime.sleep(1.5)
#     #is_point_in_polygon()
# print("fin")
    


        
        
    
       
        

    