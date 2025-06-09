from machine import Pin, ADC, time_pulse_us 
from microdot import Microdot, Response, Request
import utime
#from test import lecture_det_metaux
from deplacements import Moteur, RobotMoteurs, MoteurPasAPas
from depart_ok import depart_ok
from utils import is_point_in_polygon, find_closest_point_polygon, calculate_cap, check_mode_auto
from cycle_evite_obstacle import cycle_evitement
from cycle_rammassage import cycle_rammassage
from time import sleep
import machine
import time


# Définition des pins
METAL_DETECTOR_PIN = 26  # Pin pour le détecteur de métaux
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
def collect_metal(MoteurPAP, RobotMoteurs, pin_aimant):
    print("Démarrage du cycle de ramassage")
    ramassage = cycle_rammassage(pin_EA=pin_aimant, MoteurPAP=MoteurPAP, RobotMoteurs=RobotMoteurs)
    if ramassage:
        print("Ramassage effectué avec succès")
    else:
        print("Échec du ramassage")
    sleep(1)
    return ramassage
    
# Boucle principale
def main_auto(CapteurGps, EcranLCD, Compas, CapteurObstacle, polygone, RobotMoteurs, MoteurPAP, pin_aimant):
    if not all([CapteurGps, EcranLCD, Compas, CapteurObstacle, RobotMoteurs, MoteurPAP]):
        while True:
            print("Un ou plusieurs capteurs/moteurs ne sont pas initialisés. Arrêt du programme.")
            if CapteurObstacle:
                distance = CapteurObstacle.mesure_distance()
                print("Distance mesurée:", distance)
            if EcranLCD:
                EcranLCD.clear()
                EcranLCD.putstr("Erreur capteurs/moteurs")
            mode_auto = check_mode_auto()
            if not mode_auto:
                print("Mode manuel détecté, arrêt de la boucle auto.")
                return
            sleep(1)
    global metal_detected
    print("Démarrage du robot ramasseur de déchets")
    
    #try:    
    while True:
        # Si un métal a été détecté par l'interruption
        if metal_detected:
            rammassage = collect_metal(MoteurPAP=MoteurPAP, RobotMoteurs=RobotMoteurs, pin_aimant=pin_aimant)
            metal_detected = False  # Réinitialiser l'état
        # Autres tâches du robot (déplacement, etc.)
        time.sleep(0.05)
        mode_auto = check_mode_auto()
        if not mode_auto:
            print("Mode manuel détecté, arrêt de la boucle auto.")
            return
        longitude, latitude = CapteurGps.read()
 
        distance = CapteurObstacle.mesure_distance()

        inside = is_point_in_polygon(lat=latitude, lon=longitude, polygon=polygone)

        if distance < 10:
            print("Obstacle détecté à moins de 10 cm")
            cycle_evitement(CapteurObstacle, RobotMoteurs)

        if not inside:
            print("Hors du polygone, retour au point de départ")
            closest_point = find_closest_point_polygon(latitude, longitude, polygone)
            cap_retour = calculate_cap(latitude, longitude, closest_point[0], closest_point[1])
            print("Cap de retour:", cap_retour)
            
            # Lecture du cap actuel
            cap_actuel = Compas.lire_cap()
            if cap_actuel is not None:
                # Calcul de la différence d'angle [-180, 180]
                diff = (cap_retour - cap_actuel + 540) % 360 - 180
                seuil_alignement = 10  # degrés de tolérance

                if abs(diff) <= seuil_alignement:
                    print("Aligné, j'avance")
                    RobotMoteurs.avancer()
                elif diff > 0:
                    print("Tourner à gauche")
                    RobotMoteurs.gauche()
                else:
                    print("Tourner à droite")
                    RobotMoteurs.droite()
            else:
                print("Impossible de lire le cap, arrêt")
                RobotMoteurs.stop()
        RobotMoteurs.avancer()
        sleep(0.5)












