from time import sleep
from machine import Pin
from deplacements import MoteurPasAPas, RobotMoteurs


def cycle_rammassage(pin_EA, MoteurPAP, RobotMoteurs):
    try:
        moteur = MoteurPAP
        robot = RobotMoteurs
        ea = pin_EA 
        
        print("Test avec pas complet...")
        moteur.set_step_mode("full")
        moteur.tourner_angle(15, delay=0.02, direction=-1)
        ea.value(1)
        robot.avancer()
        sleep(4)
        moteur.tourner_angle(35, delay=0.02, direction=1)
        ea.value(0)
        sleep(1)
        moteur.stop()
        return True
    except Exception as e:
        print(f"Erreur lors du cycle de ramassage: {e}")
        return False

