import utime
from machine import I2C, Pin
import machine
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

def init_lcd(I2C_ADDR = 39, I2C_NUM_ROWS = 2, I2C_NUM_COLS = 16, sda_pin=4, scl_pin=5):
    
    i2c = I2C(0, sda=machine.Pin(sda_pin), scl=machine.Pin(scl_pin), freq=400000)
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
    return lcd


# lcd = init_lcd()
# lcd.move_to(0,0)
# lcd.putstr("Custom Character")