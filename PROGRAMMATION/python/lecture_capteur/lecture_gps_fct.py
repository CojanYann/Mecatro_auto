from micropyGPS import MicropyGPS
from time import *
import machine
import utime

print("start")

# Initialisation de l'UART0 pour le module GPS
uart = machine.UART(0, baudrate=9600, rx=machine.Pin(1), tx=machine.Pin(0))  # TX sur GPIO 1, RX sur GPIO 0
gps = MicropyGPS()
satellite_bool = 1

# Fonction pour convertir les coordonnées en format décimal
def convert_to_decimal(coord):
    degrees = coord[0]
    minutes = coord[1]
    direction = coord[2]
    decimal = degrees + (minutes / 60)
    if direction in ('S', 'W'):  # Sud ou Ouest doivent être négatifs
        decimal *= -1
    return decimal

def lecture_gps(gps, uart, satellite_bool):
    while True:
        if uart.any():
            data = uart.read(32)  # Lire jusqu'à 32 octets depuis le GPS
            if satellite_bool == 1:
                print("Satellites visibles:", gps.satellites_in_use)
            for byte in data:
                gps.update(chr(byte))  # Mise à jour des données GPS avec chaque caractère

            if gps.valid:
                # Conversion des coordonnées
                latitude_decimal = convert_to_decimal(gps.latitude)
                longitude_decimal = convert_to_decimal(gps.longitude)	
                return(latitude_decimal, longitude_decimal)

            else:
                return("Données GPS invalides.")
        else:
            return("Aucune donnée GPS.")

for i in range(40):	
    print("lecture")
    coord = lecture_gps(gps, uart, satellite_bool)
    print(coord)
    utime.sleep(1)
