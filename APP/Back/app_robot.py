from microdot import Microdot, Response, Request
from machine import I2C, Pin
import network
import machine
import time
import json
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from depart_ok import depart_ok
import socket

# --- Configuration LCD ---
GPS, LCD, COMPAS, C_OBSTACLE = depart_ok()

LCD = False
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
        if LCD:
            LCD.clear()
            LCD.putstr("IP:")
            LCD.putstr(ip)
        return ip
    else:
        print("Échec de connexion Wi-Fi")
        if LCD:
            LCD.clear()
            LCD.putstr("WiFi: ECHEC")
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

# --- Application Web ---
app = Microdot()
Response.default_content_type = 'text/html'

# --- Variables d'état ---
robot_state = {
    "mode": "manuel",  # manuel ou auto
    "battery": 75,     # pourcentage de batterie simulé
    "power": True      # état d'alimentation (on/off)
}

# Position GPS initiale
try:
    lon, lat = GPS.read()
    robot_position = {"lat": lat, "lng": lon}
except Exception:
    robot_position = {"lat": None, "lng": None}

# Fonction qui serait appelée en mode auto (simulation)
def auto_mode():
    print("Mode automatique activé - Le robot fonctionne de manière autonome")
    # Ici vous ajouteriez le code pour le comportement autonome
    # Par exemple, la détection et le ramassage de déchets

# --- Servir les fichiers statiques ---
@app.route('/index.html')
def index(request):
    try:
        with open('index.html', 'r') as file:
            return file.read(), 200, {'Content-Type': 'text/html'}
    except:
        return "Fichier index.html non trouvé", 404

@app.route('/map.html')
def map_html(request):
    try:
        with open('map.html', 'r') as file:
            return file.read(), 200, {'Content-Type': 'text/html'}
    except:
        return "Fichier map.html non trouvé", 404

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

@app.route('/js/map.js')
def js_map(request):
    try:
        with open('js/map.js', 'r') as file:
            return file.read(), 200, {'Content-Type': 'text/javascript'}
    except:
        return "Fichier map.js non trouvé", 404

# --- Routes API ---
@app.route('/api/mode', methods=['GET'])
def get_mode(request):
    return Response(json.dumps({"mode": robot_state["mode"]}), 
                   headers={'Content-Type': 'application/json'})

@app.route('/api/mode/auto', methods=['POST'])
def set_auto(request):
    robot_state["mode"] = "auto"
    print("🤖 Mode automatique activé")
    if LCD:
        LCD.clear()
        LCD.putstr("Mode: AUTO")
    
    # Appel à la fonction de mode automatique (serait remplacé par votre propre logique)
    auto_mode()
    
    return Response(json.dumps({"status": "ok", "mode": "auto"}))

@app.route('/api/mode/manual', methods=['POST'])
def set_manual(request):
    robot_state["mode"] = "manuel"
    print("🔧 Mode manuel activé")
    if LCD:
        LCD.clear()
        LCD.putstr("Mode: MANUEL")
    
    return Response(json.dumps({"status": "ok", "mode": "manuel"}))

@app.route('/api/status', methods=['GET'])
def get_status(request):
    return Response(json.dumps(robot_state), 
                   headers={'Content-Type': 'application/json'})

# Routes de commande de mouvement (simplifiées)
@app.route('/api/move/<direction>', methods=['POST'])
def move(request, direction):
    if robot_state["mode"] == "manuel" and robot_state["power"]:
        # Traiter la commande de mouvement
        print(f"Mouvement: {direction}")
        # Affichage sur le LCD selon la direction
        if LCD:
            LCD.clear()
            direction_map = {
                "forward": "Avancer",
                "backward": "Reculer",
                "left": "Gauche",
                "right": "Droite",
                "stop": "Stop"
            }
            LCD.putstr(direction_map.get(direction, direction))
        # Ici on ajouterait le code pour contrôler les moteurs
        return Response(json.dumps({"status": "ok", "action": f"move_{direction}"}), 'application/json')
    else:
        return Response(json.dumps({"status": "error", "message": "Le robot ne peut pas être contrôlé manuellement dans ce mode"}), 'application/json', 400)

# API pour la position du robot
@app.route('/api/coordrobot/', methods=['GET', 'POST'])
def coordrobot(request):
    global robot_position
    if request.method == 'POST':
        data = request.json
        if data and "lat" in data and "lng" in data:
            robot_position["lat"] = data["lat"]
            robot_position["lng"] = data["lng"]
            return Response(json.dumps({"status": "ok"}), headers={'Content-Type': 'application/json'})
        return Response(json.dumps({"status": "error", "message": "lat/lng manquants"}), headers={'Content-Type': 'application/json'}), 400
    else:
        # Mise à jour de la position GPS à chaque GET
        try:
            lon, lat = GPS.read()
            robot_position["lat"] = lat
            robot_position["lng"] = lon
        except Exception:
            robot_position["lat"] = None
            robot_position["lng"] = None
        return Response(json.dumps(robot_position), headers={'Content-Type': 'application/json'})
    
gps_coords = {"coords": []}

@app.route('/api/coordgsp/', methods=['GET', 'POST'])
def coordgsp(request):
    global gps_coords
    if request.method == 'POST':
        data = request.json
        if data and "coords" in data:
            gps_coords["coords"] = data["coords"]
        return Response(json.dumps({"status": "ok"}), headers={'Content-Type': 'application/json'})
    else:
        return Response(json.dumps(gps_coords), headers={'Content-Type': 'application/json'})

# --- Lancer le serveur ---
def start_server():
    try:
        print(f"Démarrage du serveur sur http://{ip_address}:80")
        if LCD:
            LCD.clear()
            LCD.putstr("Serveur: ON")
            LCD.putstr(f"IP: {ip_address}")
        app.run(host="0.0.0.0", port=80)
    except Exception as e:
        print(f"Erreur serveur: {e}")
        if LCD:
            LCD.clear()
            LCD.putstr("Erreur serveur")

if __name__ == "__main__":
    start_server()