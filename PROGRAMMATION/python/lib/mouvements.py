
from machine import Pin, PWM
from time import sleep

def init_moteur(M1_IN1=11, M1_IN2=12, M1_PWM=13, M2_IN1=9, M2_IN2=10, M2_PWM=8):
    IN1 = Pin(M1_IN1, Pin.OUT)
    IN2 = Pin(M1_IN2, Pin.OUT)
    vitesseMoteurA = PWM(Pin(M1_PWM) , freq=1000)

    IN3 = Pin(M2_IN1, Pin.OUT)
    IN4 = Pin(M2_IN2, Pin.OUT)
    vitesseMoteurB = PWM(Pin(M2_PWM) , freq=1000)
    return vitesseMoteurA, vitesseMoteurB, IN1, IN2, IN3, IN4

vitesseMoteurA, vitesseMoteurB, IN1, IN2, IN3, IN4 = init_moteur()
#le temps de cycle se regle entre [0-65535]
def vitesse(vit):
    vitesseMoteurA.duty_u16(vit)
    vitesseMoteurB.duty_u16(vit)


def av():
    IN1.low()  
    IN2.high()
    IN3.low()  
    IN4.high()



def arr():
    IN2.low()  
    IN1.high()
    IN4.low()  
    IN3.high()


def gauche():
    IN1.low()  
    IN2.high()
    IN4.low()  
    IN3.high()

def droite():
    IN2.low()  
    IN1.high()
    IN3.low()  
    IN4.high()


    
def stop():
    IN1.low()  
    IN2.low()
    IN3.low()  
    IN4.low()
    
vitesse(40000)
av()
sleep(2)
stop()
sleep(2)
arr()
sleep(2)
stop()
    

