import utime
from machine import I2C, Pin
import machine
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

class LCD:
    def __init__(self, I2C_ADDR=39, I2C_NUM_ROWS=2, I2C_NUM_COLS=16, sda_pin=4, scl_pin=5):
        i2c = I2C(0, sda=machine.Pin(sda_pin), scl=machine.Pin(scl_pin), freq=400000)
        self.lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

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

# Exemple d'utilisation :
if __name__ == "__main__":
    lcd = LCD()
    lcd.display_message("Custom Character")