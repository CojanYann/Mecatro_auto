from machine import ADC, Pin
import utime
import time


def check_detector(timer, threshold):
    global metal_detected
    value = detector_pin.read_u16()
    if value > threshold:
        metal_detected = True
        print("Métal détecté! Valeur:", value)
        
#Sensibilité detecteur 2 clic
def lecture_det_metaux():
    # Configuration du port ADC0 (GPIO26)
    adc = ADC(Pin(26))
    valeur = adc.read_u16()  # Lecture ADC (0-65535)
    tension = (valeur / 65535) * 3.3  # Conversion en volts
    if tension > 0.6:
        print("Tension:", tension, "V")
        return True
    return False

# i= 0
# print("start")
# while True:
#     a = lecture_det_metaux()
#     if a:
#         i+=1
#         time.sleep(0.5)
#     if i > 100:
#         break
# print("fin")