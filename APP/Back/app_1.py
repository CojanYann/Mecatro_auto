from microdot import Microdot, Response
from machine import I2C, Pin
import network
import machine
import time
import json
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

# --- Configuration LCD ---
def init_lcd(I2C_ADDR = 39, I2C_NUM_ROWS = 2, I2C_NUM_COLS = 16, sda_pin=4, scl_pin=5):
    i2c = I2C(0, sda=machine.Pin(sda_pin), scl=machine.Pin(scl_pin), freq=400000)
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
    return lcd

try:
    lcd = init_lcd()
    lcd.clear()
    lcd.putstr("Demarrage...")
    lcd_available = True
except Exception as e:
    print("Erreur LCD:", e)
    lcd_available = False

# --- Connexion Wi-Fi ---
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print(f"Connexion au réseau Wi-Fi: {ssid}")
    
    wlan.connect(ssid, password)
    
    # Attendre la connexion avec timeout
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
        if lcd_available:
            lcd.clear()
            lcd.putstr("IP:")
            lcd.putstr(ip)
        return ip
    else:
        print("Échec de connexion Wi-Fi")
        if lcd_available:
            lcd.clear()
            lcd.putstr("WiFi: ECHEC")
        return None

# Modifier ces paramètres pour votre réseau Wi-Fi
ip_address = connect_wifi("OnePlus 6", "12345678")

# --- Application Web ---
app = Microdot()
Response.default_content_type = 'text/html'

# --- Variables d'état ---
robot_state = {
    "mode": "manuel",  # manuel ou auto
    "battery": 75,     # pourcentage de batterie simulé
    "power": True      # état d'alimentation (on/off)
}

# Fonction qui serait appelée en mode auto (simulation)
def auto_mode():
    print("Mode automatique activé - Le robot fonctionne de manière autonome")
    # Ici vous ajouteriez le code pour le comportement autonome
    # Par exemple, la détection et le ramassage de déchets

# --- Servir les fichiers statiques ---
@app.route('/')
def index(request):
    try:
        with open('index.html', 'r') as file:
            return file.read(), 200, {'Content-Type': 'text/html'}
    except:
        return "Fichier index.html non trouvé", 404

@app.route('/css/style.css')
def css(request):
    try:
        with open('css/style.css', 'r') as file:
            return file.read(), 200, {'Content-Type': 'text/css'}
    except:
        return "Fichier CSS non trouvé", 404

@app.route('/js/main.js')
def js(request):
    try:
        with open('js/main.js', 'r') as file:
            return file.read(), 200, {'Content-Type': 'text/javascript'}
    except:
        return "Fichier JavaScript non trouvé", 404

# --- Routes API ---
@app.route('/api/mode', methods=['GET'])
def get_mode(request):
    return Response(json.dumps({"mode": robot_state["mode"]}), 
                   content_type='application/json')

@app.route('/api/mode/auto', methods=['POST'])
def set_auto(request):
    robot_state["mode"] = "auto"
    print("🤖 Mode automatique activé")
    if lcd_available:
        lcd.clear()
        lcd.putstr("Mode: AUTO")
    
    # Appel à la fonction de mode automatique (serait remplacé par votre propre logique)
    auto_mode()
    
    return Response(json.dumps({"status": "ok", "mode": "auto"}), 
                   content_type='application/json')

@app.route('/api/mode/manuel', methods=['POST'])
def set_manual(request):
    robot_state["mode"] = "manuel"
    print("🔧 Mode manuel activé")
    if lcd_available:
        lcd.clear()
        lcd.putstr("Mode: MANUEL")
    
    return Response(json.dumps({"status": "ok", "mode": "manuel"}), 
                   content_type='application/json')

@app.route('/api/status', methods=['GET'])
def get_status(request):
    return Response(json.dumps(robot_state), 
                   content_type='application/json')

# Routes de commande de mouvement (simplifiées)
@app.route('/api/move/<direction>', methods=['POST'])
def move(request, direction):
    if robot_state["mode"] == "manuel" and robot_state["power"]:
        # Traiter la commande de mouvement
        print(f"Mouvement: {direction}")
        # Affichage sur le LCD selon la direction
        if lcd_available:
            lcd.clear()
            direction_map = {
                "forward": "Avancer",
                "backward": "Reculer",
                "left": "Gauche",
                "right": "Droite",
                "stop": "Stop"
            }
            lcd.putstr(direction_map.get(direction, direction))
        # Ici on ajouterait le code pour contrôler les moteurs
        return Response(json.dumps({"status": "ok", "action": f"move_{direction}"}), 'application/json')
    else:
        return Response(json.dumps({"status": "error", "message": "Le robot ne peut pas être contrôlé manuellement dans ce mode"}), 'application/json', 400)

# --- Lancer le serveur ---
def start_server():
    try:
        print(f"Démarrage du serveur sur http://{ip_address}:80")
        if lcd_available:
            lcd.clear()
            lcd.putstr("Serveur: ON")
            lcd.putstr(f"IP: {ip_address}")
        app.run(host="0.0.0.0", port=80)
    except Exception as e:
        print(f"Erreur serveur: {e}")
        if lcd_available:
            lcd.clear()
            lcd.putstr("Erreur serveur")

if __name__ == "__main__":
    start_server()