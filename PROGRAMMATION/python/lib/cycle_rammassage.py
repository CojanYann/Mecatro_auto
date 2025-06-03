from time import sleep
from machine import Pin
from deplacements import MoteurPAP, RobotMoteurs


def cycle_rammassage(pin_EA, MoteurPAP, RobotMoteurs):
    try:
        MoteurPAP.step_motor(200, delay=0.01, direction=1)
        pin_EA.value(1)
        RobotMoteurs.avancer()
        sleep(1.5)
        MoteurPAP.step_motor(200, delay=0.01, direction=0)
        pin_EA.value(0)
        return True
    except Exception as e:
        print(f"Erreur lors du cycle de ramassage: {e}")
        return False

