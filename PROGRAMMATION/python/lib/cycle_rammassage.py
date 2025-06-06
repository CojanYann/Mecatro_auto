from time import sleep
from machine import Pin
from deplacements import MoteurPasAPas, RobotMoteurs


def cycle_rammassage(pin_EA, MoteurPAP, RobotMoteurs):
    try:
        moteur = MoteurPAP
        
        print("Test avec pas complet...")
        moteur.set_step_mode("full")
        moteur.step_motor(200, delay=0.003, direction=1)
        sleep(1)
        moteur.step_motor(200, delay=0.003, direction=-1)
        return True
    except Exception as e:
        print(f"Erreur lors du cycle de ramassage: {e}")
        return False

