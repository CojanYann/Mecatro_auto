from time import sleep
from machine import Pin
from deplacements import MoteurPAP, RobotMoteurs


def cycle_rammassage(pin_EA, MoteurPAP, RobotMoteurs):
    try:
        MoteurPAP.descendre()
        pin_EA.value(1)
        RobotMoteurs.avancer()
        sleep(1.5)
        MoteurPAP.monter()
        pin_EA.value(0)
        return True
    except Exception as e:
        print(f"Erreur lors du cycle de ramassage: {e}")
        return False

