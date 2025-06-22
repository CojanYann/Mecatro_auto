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
    """
    Classe pour contrôler un moteur pas à pas bipolaire (comme le SY42STH47)
    avec un driver L298N
    
    Connexions L298N:
    - IN1 -> Bobinage A (sens 1)
    - IN2 -> Bobinage A (sens 2) 
    - IN3 -> Bobinage B (sens 1)
    - IN4 -> Bobinage B (sens 2)
    - ENA et ENB -> 3.3V (toujours activés)
    """
    def __init__(self, in1=16, in2=17, in3=18, in4=19):
        self.IN1 = Pin(in1, Pin.OUT)  # Bobinage A - Direction 1
        self.IN2 = Pin(in2, Pin.OUT)  # Bobinage A - Direction 2
        self.IN3 = Pin(in3, Pin.OUT)  # Bobinage B - Direction 1
        self.IN4 = Pin(in4, Pin.OUT)  # Bobinage B - Direction 2
        
        # Séquence pour moteur bipolaire (full step)
        # [A+, A-, B+, B-]
        self.sequence_full = [
            [1, 0, 1, 0],  # A+, B+
            [0, 1, 1, 0],  # A-, B+
            [0, 1, 0, 1],  # A-, B-
            [1, 0, 0, 1]   # A+, B-
        ]
        
        # Séquence demi-pas pour plus de précision
        self.sequence_half = [
            [1, 0, 1, 0],  # A+, B+
            [1, 0, 0, 0],  # A+ seulement
            [0, 1, 1, 0],  # A-, B+
            [0, 0, 1, 0],  # B+ seulement
            [0, 1, 0, 1],  # A-, B-
            [0, 0, 0, 1],  # B- seulement
            [1, 0, 0, 1],  # A+, B-
            [0, 0, 0, 0]   # Pause
        ]
        
        # Utiliser la séquence de pas complet par défaut
        self.sequence = self.sequence_full
        
    def set_step_mode(self, mode="full"):
        """Changer le mode de pas"""
        if mode == "full":
            self.sequence = self.sequence_full
        elif mode == "half":
            self.sequence = self.sequence_half
    
    def step_motor(self, steps, delay=0.01, direction=1):
        """
        steps: nombre de pas
        delay: délai entre chaque pas (en secondes) - minimum 0.01s pour SY42STH47
        direction: 1 pour horaire, -1 pour anti-horaire
        """
        sequence_to_use = self.sequence if direction == 1 else list(reversed(self.sequence))
        
        for _ in range(steps):
            for step in sequence_to_use:
                self.IN1.value(step[0])  # Bobinage A direction 1
                self.IN2.value(step[1])  # Bobinage A direction 2
                self.IN3.value(step[2])  # Bobinage B direction 1
                self.IN4.value(step[3])  # Bobinage B direction 2
                sleep(delay)
    
    def stop(self):
        """Arrêter le moteur et couper l'alimentation"""
        self.IN1.value(0)
        self.IN2.value(0)
        self.IN3.value(0)
        self.IN4.value(0)

    def tourner_angle(self, angle, delay=0.01, direction=1):
        """
        Tourner d'un angle spécifique
        angle: angle en degrés
        Le SY42STH47 a un pas de 1.8° donc 200 pas = 360°
        """
        steps_per_revolution = 200  # 360° / 1.8° par pas
        steps = int((angle / 360.0) * steps_per_revolution)
        self.step_motor(steps, delay, direction)

# Exemple d'utilisation corrigée
if __name__ == "__main__":
#     # Utiliser la nouvelle classe pour moteur bipolaire
     print("demmarage")
     moteur = MoteurPasAPas()
 
     moteur.set_step_mode("half")
    #moteur.step_motor(20)
     moteur.tourner_angle(35, delay=0.01, direction=1)
     moteur.tourner_angle(10, delay=0.005, direction=-1)  # 200 pas = 1 tour
     sleep(3)
     moteur.tourner_angle(25, delay=0.01, direction=1)
     sleep(3)
 
     
     # Arrêter le moteur
     moteur.stop()
     
     print("Tests terminés!")
#     print("depart")
#     moteur = RobotMoteurs()
#     moteur.avancer()
#     sleep(2)
#  
#     moteur.stop()




