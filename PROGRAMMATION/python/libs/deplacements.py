from machine import Pin, PWM
from time import sleep

class Moteur:
    def __init__(self, in1, in2, pwm, freq=1000):
        self.IN1 = Pin(in1, Pin.OUT)
        self.IN2 = Pin(in2, Pin.OUT)
        self.pwm = PWM(Pin(pwm), freq=freq)
        self.vitesse(0)

    def avance(self):
        self.IN1.low()
        self.IN2.high()

    def recule(self):
        self.IN2.low()
        self.IN1.high()

    def stop(self):
        self.IN1.low()
        self.IN2.low()

    def vitesse(self, vit):
        self.pwm.duty_u16(vit)

class RobotMoteurs:
    def __init__(self, 
                 M1_IN1=11, M1_IN2=12, M1_PWM=13, 
                 M2_IN1=9, M2_IN2=10, M2_PWM=8):
        self.moteurA = Moteur(M1_IN1, M1_IN2, M1_PWM)
        self.moteurB = Moteur(M2_IN1, M2_IN2, M2_PWM)

    def vitesse(self, vit):
        self.moteurA.vitesse(vit)
        self.moteurB.vitesse(vit)

    def avancer(self):
        self.moteurA.avance()
        self.moteurB.avance()

    def reculer(self):
        self.moteurA.recule()
        self.moteurB.recule()

    def gauche(self):
        self.moteurA.recule()
        self.moteurB.avance()

    def droite(self):
        self.moteurA.avance()
        self.moteurB.recule()

    def stop(self):
        self.moteurA.stop()
        self.moteurB.stop()

# Exemple d'utilisation
if __name__ == "__main__":
    robot = RobotMoteurs()
    robot.vitesse(40000)
    robot.avancer()
    sleep(2)
    robot.stop()
    sleep(2)
    robot.reculer()
    sleep(2)
    robot.stop()


