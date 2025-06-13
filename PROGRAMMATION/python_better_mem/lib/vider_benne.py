from machine import Pin,PWM
from time import sleep
import time

class ServoBenne:
    def __init__(self, pin=28, freq=50):
        self.sg = PWM(Pin(pin, mode=Pin.OUT))
        self.sg.freq(freq)
        self.duty_cycle = 0
        self.a=6500
        self.b=3000
  
    def descendre(self):
        for i in range(self.a,self.b,-100):
            self.sg.duty_u16(i)
            time.sleep(0.01) #compteur incrémental pour bouger la porte en douceur 

    def monter(self):
        for i in range(self.b,self.a,100):
            self.sg.duty_u16(i)
            time.sleep(0.01)
    def stop(self):
        self.sg.duty_u16(self.a)
        
def cycle_vider_bac(servo): 
    try:
        servo.descendre()  # Ouvre la benne
        sleep(2)           # Attendre 2 secondes pour vider la benne
        servo.monter()     # Ferme la benne
    except KeyboardInterrupt:
        print("Opération interrompue par l'utilisateur.")
    finally:
        servo.stop()  # Nettoyage du PWM
        print("Servo désactivé.")
if __name__ == "__main__":
    servo = ServoBenne(pin=28)
    cycle_vider_bac(servo)  # Exécute le cycle de descente et montée de la benne
    print("Cycle terminé.")
