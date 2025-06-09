from time import sleep
from machine import Pin
from deplacements import MoteurPasAPas, RobotMoteurs


def cycle_rammassage(pin_EA, MoteurPAP, RobotMoteurs):
    try:
        moteur = MoteurPAP
        
        print("Test avec pas complet...")
        moteur.set_step_mode("full")
        moteur.step_motor(100, delay=0.004, direction=1)
        moteur.stop()
        sleep(1)
        moteur.step_motor(100, delay=0.004, direction=-1)
        moteur.stop()
        return True
    except Exception as e:
        print(f"Erreur lors du cycle de ramassage: {e}")
        return False

