import utime
from time import sleep
import machine
from machine import I2C
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

class LCD:
    def __init__(self, i2c_addr=0x27, num_rows=4, num_cols=16, sda_pin=4, scl_pin=5, freq=400000):
        self.i2c_addr = i2c_addr
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.sda_pin = sda_pin
        self.scl_pin = scl_pin
        # Correction : passer directement les paramètres au constructeur I2cLcd
        # Le constructeur I2cLcd crée lui-même l'objet I2C en interne
        self.i2c = I2C(0, sda=machine.Pin(sda_pin), scl=machine.Pin(scl_pin), freq=freq)
        self.lcd = I2cLcd(self.i2c, i2c_addr, num_rows, num_cols)
    
    def clear(self):
        self.lcd.clear()
    
    def move_to(self, col, row):
        self.lcd.move_to(col, row)
    
    def putstr(self, string):
        self.lcd.putstr(string)
    
    def display_message(self, message, col=0, row=0, clear_first=True):
        if clear_first:
            self.clear()
        self.move_to(col, row)
        self.putstr(message)
    
    def is_connected(self):
        try:
            self.clear()
            return True
        except Exception:
            return False

if __name__ == "__main__":
    from machine import I2C, Pin
    i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
    devices = i2c.scan()

    print("I2C devices found:", devices)

    if 0x27 not in devices:
        print("Erreur : écran LCD non détecté à l’adresse 0x27 !")
    else:
        lcd = LCD()
        lcd.putstr("LCD Test")
        sleep(2)
        lcd.clear()
        lcd.putstr("hello world")
        sleep(2)
        lcd.clear()

    
