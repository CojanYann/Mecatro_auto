from machine import Pin, ADC, time_pulse_us
import utime
#from test import lecture_det_metaux
from deplacements import Moteur, RobotMoteurs
from depart_ok import depart_ok
from utils import is_point_in_polygon, find_closest_point_polygon, calculate_cap
from cycle_evite_obstacle import cycle_evitement
from time import sleep
import machine
import time

# Définition des pins
METAL_DETECTOR_PIN = 26  # Pin pour le détecteur de métaux
# Autres pins (moteurs, etc.)
polygone = [
    (47.571300, -3.072753),
    (47.571389, -3.072347),
    (47.571595, -3.071556),
    (47.571357, -3.071503),
    (47.571164, -3.072600)
]
# Variable pour suivre l'état de détection
metal_detected = False

# Initialisation des capteurs
result = depart_ok()
if not result:
    print("Erreur d'initialisation des capteurs. Arrêt du programme.")
    RobotMoteurs = None
    CapteurGps = EcranLCD = Compas = CapteurObstacle = None
else:
    CapteurGps, EcranLCD, Compas, CapteurObstacle = result
    RobotMoteurs = RobotMoteurs()


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
    sleep(3)
    print("Fin du cycle de ramassage")
    
# Boucle principale
def main(CapteurGps, EcranLCD, Compas, CapteurObstacle, polygone, RobotMoteurs):

    global metal_detected
    print("Démarrage du robot ramasseur de déchets")
    
    #try:    
    while True:
        # Si un métal a été détecté par l'interruption
        if metal_detected:
            collect_metal()
            metal_detected = False  # Réinitialiser l'état
        # Autres tâches du robot (déplacement, etc.)
        time.sleep(0.1)
        longitude, latitude = CapteurGps.read()
        print("on est la")
        distance = CapteurObstacle.mesure_distance()
        print("on est la2", longitude, latitude, polygone)
        inside = is_point_in_polygon(lat=latitude, lon=longitude, polygon=polygone)
        print("on est la3")
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

        
    # except KeyboardInterrupt:
    #     print("Programme arrêté par l'utilisateur")
    # finally:
    #     if RobotMoteurs:
    #         RobotMoteurs.stop()
    #         print("Moteurs arrêtés")

if __name__ == "__main__":
    main(CapteurGps, EcranLCD, Compas, CapteurObstacle, polygone=polygone, RobotMoteurs=RobotMoteurs)










