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

class MoteurPasAPas:
    def __init__(self, in1=16, in2=17, in3=18, in4=19):
        self.IN1 = Pin(in1, Pin.OUT)
        self.IN2 = Pin(in2, Pin.OUT)
        self.IN3 = Pin(in3, Pin.OUT)
        self.IN4 = Pin(in4, Pin.OUT)
        self.sequence = [
            [1, 0, 1, 0],
            [0, 1, 1, 0],
            [0, 1, 0, 1],
            [1, 0, 0, 1] 
        ]

    def step_motor(self, steps, delay=0.01, direction=1):
        for _ in range(steps):
            for step in (self.sequence if direction == 1 else reversed(self.sequence)):
                self.IN1.value(step[0])
                self.IN2.value(step[1])
                self.IN3.value(step[2])
                self.IN4.value(step[3])
                sleep(delay)


# Exemple d'utilisation
if __name__ == "__main__":
    robot = RobotMoteurs()
    Moteurpasapas = MoteurPasAPas()
    robot.vitesse(40000)
    robot.avancer()
    Moteurpasapas.step_motor(200, delay=0.01, direction=1)
    sleep(2)
    robot.stop()
    Moteurpasapas.step_motor(200, delay=0.01, direction=0)
    sleep(2)
    robot.reculer()
    sleep(2)
    robot.stop()


