from machine import Pin, ADC, time_pulse_us 
from microdot import Microdot, Response, Request
import utime
#from test import lecture_det_metaux
from deplacements import Moteur, RobotMoteurs, MoteurPasAPas
from depart_ok import depart_ok
from utils import is_point_in_polygon, find_closest_point_polygon, calculate_cap
from cycle_evite_obstacle import cycle_evitement
from cycle_rammassage import cycle_rammassage
from time import sleep
import machine
import time


# Définition des pins
METAL_DETECTOR_PIN = 26  # Pin pour le détecteur de métaux
BUTTON_PIN = 22          # Pin pour le bouton physique
metal_detected = False
mode_auto_active = False  # Ajout pour savoir si on est en mode auto

# Initialisation du bouton (entrée avec pull-up)
button_pin = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
last_button_state = 1
last_button_time = 0

# Fonction utilitaire pour remettre metal_detected à False après 5s en mode manuel
def reset_metal_detected_timer():
    global metal_detected
    time.sleep(5)
    metal_detected = False
    print("Fin affichage détection métal (manuel)")

# Fonction de callback pour l'interruption
def metal_detection_callback(pin):
    global metal_detected, mode_auto_active
    if mode_auto_active:
        # En mode auto, on lance le ramassage immédiatement
        metal_detected = True
        print("Métal détecté! (auto)")
        # collect_metal sera appelé dans la boucle principale (pas ici pour éviter thread/conflit)
    else:
        # En mode manuel, on signale la détection pendant 5 secondes
        if not metal_detected:
            metal_detected = True
            print("Métal détecté! (manuel, affichage 5s)")
            import _thread
            _thread.start_new_thread(reset_metal_detected_timer, ())


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
    global metal_detected, mode_auto_active
    mode_auto_active = True  # On entre en mode auto
    if not all([CapteurGps, EcranLCD, Compas, CapteurObstacle, RobotMoteurs, MoteurPAP]):
        last_button_state = 1
        last_button_time = time.ticks_ms()
        while True:
            # Gestion du bouton physique (broche 22)
            button_state = button_pin.value()
            now = time.ticks_ms()
            if last_button_state == 1 and button_state == 0 and time.ticks_diff(now, last_button_time) > 300:
                print("Bouton physique appuyé ! Sortie du mode auto (capteurs manquants).")
                return
            last_button_state = button_state
            print("Un ou plusieurs capteurs/moteurs ne sont pas initialisés. Arrêt du programme.")
            if CapteurObstacle:
                distance = CapteurObstacle.mesure_distance()
                print("Distance mesurée:", distance)
            if metal_detected:
                print("Métal détecté, mais le robot ne peut pas ramasser.")
                metal_detected = False  # Réinitialiser l'état
            if EcranLCD:
                EcranLCD.clear()
                EcranLCD.putstr("Erreur capteurs/moteurs")
            sleep(1)
    print("Démarrage du robot ramasseur de déchets")
    
    #try:    
    last_button_state = 1
    last_button_time = time.ticks_ms()
    while True:
        # Gestion du bouton physique (broche 22)
        button_state = button_pin.value()
        now = time.ticks_ms()
        if last_button_state == 1 and button_state == 0 and time.ticks_diff(now, last_button_time) > 300:
            print("Bouton physique appuyé ! Sortie du mode auto.")
            return
        last_button_state = button_state

        # Si un métal a été détecté par l'interruption
        if metal_detected:
            rammassage = collect_metal(MoteurPAP=MoteurPAP, RobotMoteurs=RobotMoteurs, pin_aimant=pin_aimant)
            metal_detected = False  # Réinitialiser l'état
        # Autres tâches du robot (déplacement, etc.)
        time.sleep(0.05)
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












