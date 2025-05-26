from machine import I2C, Pin
import network
import machine
import time
import json
import socket
import gc

# --- Connexion Wi-Fi ---
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print(f"Connexion au réseau Wi-Fi: {ssid}")
    wlan.connect(ssid, password)
    max_wait = 10
    while max_wait > 0:
        if wlan.isconnected():
            break
        max_wait -= 1
        print("Attente de connexion...")
        time.sleep(1)
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print(f"Connecté avec l'adresse IP: {ip}")
        return ip
    else:
        print("Échec de connexion Wi-Fi")
        return None

def test_internet():
    try:
        addr = socket.getaddrinfo('tile.openstreetmap.org', 80)[0][-1]
        s = socket.socket()
        s.settimeout(3)
        s.connect(addr)
        s.close()
        print("Connexion Internet OK depuis la Pico")
    except Exception as e:
        print("Pas d'accès Internet depuis la Pico:", e)

# Modifier ces paramètres pour votre réseau Wi-Fi
ip_address = connect_wifi("OnePlus 6", "12345678")
test_internet()
