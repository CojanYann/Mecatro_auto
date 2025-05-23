from micropyGPS import MicropyGPS
from grove_lcd_i2c import *
import machine
import utime

# Initialisation de l'UART0 pour le module GPS
uart = machine.UART(0, baudrate=9600, rx=machine.Pin(1), tx=machine.Pin(0))  # TX sur GPIO 1, RX sur GPIO 0
gps = MicropyGPS()
lcd = Grove_LCD_I2C()
lcd.clear()

# Fonction pour convertir les coordonnées en format décimal
def convert_to_decimal(coord):
    degrees = coord[0]
    minutes = coord[1]
    direction = coord[2]
    decimal = degrees + (minutes / 60)
    if direction in ('S', 'W'):  # Sud ou Ouest doivent être négatifs
        decimal *= -1
    return decimal

while True:
    if uart.any():
        data = uart.read(32)  # Lire jusqu'à 32 octets depuis le GPS
        print("Satellites visibles:", gps.satellites_in_use)
        for byte in data:
            gps.update(chr(byte))  # Mise à jour des données GPS avec chaque caractère

        if gps.valid:
            # Conversion des coordonnées
            latitude_decimal = convert_to_decimal(gps.latitude)
            longitude_decimal = convert_to_decimal(gps.longitude)

            # Affichage des données
            print("Latitude (décimal):", latitude_decimal)
            print("Longitude (décimal):", longitude_decimal)

            lcd.home()#retour en haut à gauche de l'écran                    
            #lcd.write('Angle/North')
            lcd.clear()
            lcd.cursor_position(0, 0)
            lcd.write(str(float(latitude_decimal)))
            lcd.cursor_position(0, 1) #passe a la ligne
            lcd.write(str(float(longitude_decimal)))
        else:
            longitude_decimal = convert_to_decimal(gps.longitude)
            print("Longitude (décimal):", gps.longitude)
            print("Données GPS invalides.")
    else:
        print("Aucune donnée GPS.")
    utime.sleep(1.3)
