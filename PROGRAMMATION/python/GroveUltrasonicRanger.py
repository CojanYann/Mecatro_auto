from machine import Pin
import utime
import time

def get_distance(pin_number):
    
    Pin(pin_number, Pin.OUT).low()
    utime.sleep_us(2)
    Pin(pin_number, Pin.OUT).high()
    utime.sleep_us(5)
    Pin(pin_number, Pin.OUT).low()
    
    signaloff = 0
    signalon = 0
    
    while Pin(pin_number, Pin.IN).value() == 0:
        signaloff = utime.ticks_us()
    while Pin(pin_number, Pin.IN).value() == 1:
        signalon = utime.ticks_us()
    
    timepassed = signalon - signaloff
    distance = (timepassed * 0.0343) / 2
    
    return distance

print("C'est parti !")
led = Pin(6, Pin.OUT)
led.low()

while True:
    
    distanceLue = get_distance(pin_number=3) #le capteur est branché sur la broche n° 1
    print("The distance from object is", distanceLue, "cm")
    
    if distanceLue <= 15:
        led.high()
    else :
        led.low()
        print("HOHO")
    sleep(0.4)