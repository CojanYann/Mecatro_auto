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
        
        # Séquence de pas complet (plus stable)
        self.sequence_full = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]
        
        # Séquence de demi-pas (plus de précision mais plus de vibrations)
        self.sequence_half = [
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
            [1, 0, 0, 1]
        ]
        
        # Utiliser la séquence de pas complet par défaut
        self.sequence = self.sequence_full
        
    def set_step_mode(self, mode="full"):
        """Changer le mode de pas"""
        if mode == "full":
            self.sequence = self.sequence_full
        elif mode == "half":
            self.sequence = self.sequence_half
    
    def step_motor(self, steps, delay=0.005, direction=1):
        """
        steps: nombre de pas
        delay: délai entre chaque pas (en secondes)
        direction: 1 pour horaire, -1 pour anti-horaire
        """
        sequence_to_use = self.sequence if direction == 1 else list(reversed(self.sequence))
        
        for _ in range(steps):
            for step in sequence_to_use:
                self.IN1.value(step[0])
                self.IN2.value(step[1])
                self.IN3.value(step[2])
                self.IN4.value(step[3])
                sleep(delay)
    
    def stop(self):
        """Arrêter le moteur et couper l'alimentation"""
        self.IN1.value(0)
        self.IN2.value(0)
        self.IN3.value(0)
        self.IN4.value(0)


# Exemple d'utilisation
if __name__ == "__main__":
    moteur = MoteurPasAPas()
    
    print("Test avec pas complet...")
    moteur.set_step_mode("full")
    moteur.step_motor(200, delay=0.003, direction=1)
    sleep(1)
    
    print("Test avec demi-pas...")
    moteur.set_step_mode("full")
    moteur.step_motor(400, delay=0.003, direction=-1)  # 400 demi-pas = 200 pas complets
    
    # Arrêter le moteur
    moteur.stop()

#     robot = RobotMoteurs()
#     robot.vitesse(60000)
#     robot.avancer()
# #    Moteurpasapas.step_motor(200, delay=0.01, direction=1)
#     sleep(2)
#     robot.gauche()
#     sleep(4)
#     robot.stop()
#    sleep(2)
#     robot.reculer()
#     sleep(2)
#     robot.gauche()
#     sleep(2)
#     robot.stop()


