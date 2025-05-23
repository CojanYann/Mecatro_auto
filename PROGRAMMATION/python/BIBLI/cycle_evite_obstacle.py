import random
from time import sleep

def cycle_evitement(CapteurObstacle, RobotMoteurs):
    # Recule un peu
    RobotMoteurs.reculer()
    sleep(0.5)
    RobotMoteurs.stop()
    sleep(0.2)
    # Tourne à droite ou à gauche aléatoirement jusqu'à trouver un passage libre
    direction = random.choice(['gauche', 'droite'])
    if direction == 'gauche':
        RobotMoteurs.gauche()
    else:
        RobotMoteurs.droite()
    # Tourne jusqu'à lire une distance > 50cm
    while True:
        dist = CapteurObstacle.mesure_distance()
        if dist is not None and dist > 50:
            break
        sleep(0.1)
    RobotMoteurs.stop()
    sleep(0.2)
    # Avance un peu pour finir l'évitement
    RobotMoteurs.avancer()
    sleep(1.5)
    RobotMoteurs.stop()