from machine import Pin, time_pulse_us
from time import sleep

# Configuration des broches


def mesure_distance(trig=15, echo=14):
    
    TRIG = Pin(trig, Pin.OUT)  # par exemple GPIO3
    ECHO = Pin(echo, Pin.IN)   # par exemple GPIO2

    # S'assurer que le TRIG est bas
    TRIG.value(0)
    sleep(0.002)
    
    # Envoyer une impulsion de 10 µs sur TRIG
    TRIG.value(1)
    sleep(0.00001)
    TRIG.value(0)
    
    # Mesurer la durée de l'impulsion sur ECHO (en µs)
    try:
        duration = time_pulse_us(ECHO, 1, 30000)  # timeout à 30 ms
    except OSError as e:
        print("Erreur de mesure:", e)
        return None

    # Calcul de la distance (le son va-retour → divisé par 2)
    distance_cm = (duration / 2) / 29.1
    return distance_cm

# Boucle principale
while True:
    dist = mesure_distance()
    if dist is not None:
        print(dist)
        print("Distance: {:.2f} cm".format(dist))
    else:
        print("Distance non détectée.")
    sleep(1)