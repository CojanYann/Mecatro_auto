from machine import Pin, time_pulse_us
from time import sleep

class CapteurUltrason:
    def __init__(self, trig=7, echo=6):
        self.TRIG = Pin(trig, Pin.OUT)
        self.ECHO = Pin(echo, Pin.IN)

    def mesure_distance(self):
        self.TRIG.value(0)
        sleep(0.002)
        self.TRIG.value(1)
        sleep(0.00001)
        self.TRIG.value(0)
        try:
            duration = time_pulse_us(self.ECHO, 1, 30000)
        except OSError as e:
            print("Erreur de mesure:", e)
            return None
        distance_cm = (duration / 2) / 29.1
        return distance_cm

    def is_connected(self):
        """Retourne True si le capteur répond, False sinon."""
        dist = self.mesure_distance()
        return dist is not None and dist > 0.01
    
