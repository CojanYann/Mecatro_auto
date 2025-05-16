from microdot import Microdot, Response
from machine import I2C, Pin
import network
import machine
#from doss import auto
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

# --- Configuration LCD ---
def init_lcd(I2C_ADDR = 39, I2C_NUM_ROWS = 2, I2C_NUM_COLS = 16, sda_pin=4, scl_pin=5):
    i2c = I2C(0, sda=machine.Pin(sda_pin), scl=machine.Pin(scl_pin), freq=400000)
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
    return lcd

lcd = init_lcd()
lcd.clear()

# --- Connexion Wi-Fi ---
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
    print("Connected, IP:", wlan.ifconfig()[0])
    return wlan.ifconfig()[0]

connect_wifi("OnePlus 6", "mdp")

# --- Application Web ---
app = Microdot()
Response.default_content_type = 'application/json'

# --- Variables d'état ---
mode = "manual"  # auto ou manual

# --- Routes de l'API ---
@app.post('/mode/auto')
def set_auto(request):
    global mode
    mode = "auto"
    lcd.clear()
    lcd.putstr("Mode: MANUEL")
    auto()
    return { "status": "ok", "mode": mode }

@app.post('/mode/manual')
def set_manual(request):
    global mode
    mode = "manual"
    print("🔧 Mode manuel activé.")
    lcd.clear()
    lcd.putstr("Mode: MANUEL")
    return { "status": "ok", "mode": mode }

# --- Lancer le serveur ---
app.run(host="0.0.0.0", port=80)
