from microdot import Microdot, Response, Request
from machine import I2C, Pin
import network 
import machine
import time
from time import sleep
import json
import socket
import gc
from lecture_lcd import LCD
from connection_pico_wifi import connect_wifi, test_internet
from deplacements import RobotMoteurs, MoteurPasAPas
from cycle_rammassage import cycle_rammassage
from main_auto import main_auto
from depart_ok import depart_ok

# init capteurs
# try:
#     LCD = LCD()
#     print("lcd ok")
# except Exception as e:
#     LCD = None

capteur_gps, ecran_lcd, capteur_compas, capteur_obstacle = depart_ok()

Robot_moteurs = RobotMoteurs()

MoteurPAP = MoteurPasAPas()
pin_aimant = Pin(20, Pin.OUT)

# inittialisation données

polygone = [[]]
gps_coords = {"coords": []}
robot_speed = 50
global metal_detected
# try:
#     lon, lat = GPS.read()
#     robot_position = {"lat": lat, "lng": lon}
# except Exception:
robot_position = {"lat": None, "lng": None}

# --- Connexion Wi-Fi ---

ip_address = connect_wifi(ssid="OnePlus 6", password="12345678", LCD=ecran_lcd)
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

# Ajout d'une variable globale pour la vitesse
  # valeur par défaut (en pourcentage)


# --- Routes API ---
@app.route('/api/mode', methods=['GET'])
def get_mode(request):
    return Response(json.dumps({"mode": robot_state["mode"]}), 
                   headers={'Content-Type': 'application/json'})

@app.route('/api/mode/auto', methods=['POST'])
def set_auto(request, LCD=ecran_lcd):
    robot_state["mode"] = "auto"
    print("Mode automatique activé")
    if LCD:
        LCD.clear()
        LCD.putstr("Mode: AUTO")
    
    # Appel à la fonction de mode automatique (serait remplacé par votre propre logique)
    if robot_state["mode"] == "auto":
        print("Démarrage du mode automatique")
        main_auto(CapteurGps=capteur_gps, 
                  EcranLCD=ecran_lcd, 
                  Compas=capteur_compas, 
                  CapteurObstacle=capteur_obstacle, 
                  polygone=polygone, 
                  RobotMoteurs=Robot_moteurs, 
                  MoteurPAP=MoteurPAP, 
                  pin_aimant=pin_aimant)
        # Libération mémoire explicite après chaque appel à main_auto
        gc.collect()
        # del capteur_gps, ecran_lcd, capteur_compas, capteur_obstacle, Robot_moteurs, MoteurPAP, pin_aimant
        # gc.collect()
    
    return Response(json.dumps({"status": "ok", "mode": "auto"}))

@app.route('/api/mode/manual', methods=['POST'])
def set_manual(request, ecran_lcd=ecran_lcd):
    robot_state["mode"] = "manuel"
    print("🔧 Mode manuel activé")
    if ecran_lcd:
        ecran_lcd.clear()
        ecran_lcd.putstr("Mode: MANUEL")
    
    return Response(json.dumps({"status": "ok", "mode": "manuel"}))

@app.route('/api/status', methods=['GET'])
def get_status(request):
    return Response(json.dumps(robot_state), 
                   headers={'Content-Type': 'application/json'})

# Routes de commande de mouvement (simplifiées)
@app.route('/api/move/<direction>', methods=['POST'])
def move(request, direction, RobotMoteurs=Robot_moteurs, LCD=ecran_lcd):
    if robot_state["mode"] == "manuel" and robot_state["power"]:
        # Traiter la commande de mouvement
        RobotMoteurs.vitesse(60000)  # Réglage de la vitesse par défaut
        direction_methods = {
            "forward": RobotMoteurs.avancer,
            "backward": RobotMoteurs.reculer,
            "left": RobotMoteurs.gauche,
            "right": RobotMoteurs.droite,
            "stop": RobotMoteurs.stop
        }
        methode = direction_methods.get(direction)
        if methode:
            methode()
            print(f"Mouvement: {direction} {methode.__name__}")
        else:
            print(f"Direction inconnue: {direction}")
        # Affichage sur le LCD selon la direction
        if LCD:
            LCD.clear()
            LCD.putstr(direction)
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

@app.route('/api/coordgps/', methods=['GET', 'POST'])
def coordgsp(request, LCD=ecran_lcd):
    global gps_coords
    global polygone
    if request.method == 'POST':
        data = request.json
        if data and "coords" in data:   
            gps_coords["coords"] = data["coords"]
            print(polygone)
            polygone = gps_coords["coords"]
            print("Polygone mis à jour:", polygone)
            if LCD:
                LCD.clear()
                LCD.putstr("Polygone mises à jour")
        return Response(json.dumps({"status": "ok"}), headers={'Content-Type': 'application/json'})
    else:
        return Response(json.dumps(gps_coords), headers={'Content-Type': 'application/json'})

@app.route('/api/speed', methods=['POST', 'GET'])
def set_speed(request, RobotMoteurs=Robot_moteurs, LCD=ecran_lcd):
    global robot_speed
    if request.method == 'POST':
        try:
            data = data = request.json
        except Exception:
            data = None
        speed = None
        if data:
            if 'speed' in data:
                speed = data['speed']
            elif 'description' in data:
                speed = data['description']

            print(f"Vitesse reçue: {speed}")
        if speed is None:
            speed = 50  # valeur par défaut
            print("speed is none")
        # Conversion de la vitesse en valeur PWM (0-65535)
        pwm_value = int((int(speed) / 100) * 65000)
        RobotMoteurs.vitesse(pwm_value)
        robot_speed = int(speed)  # Mémorise la dernière vitesse
        print(f"Vitesse réglée à: {speed}% (PWM={pwm_value})")
        if LCD:
            LCD.clear()
            LCD.putstr(f"Vitesse: {speed}%")
        return Response(json.dumps({"status": "ok", "speed": speed}), headers={'Content-Type': 'application/json'})
    else:  # GET
        return Response(json.dumps({"speed": robot_speed}), headers={'Content-Type': 'application/json'})

@app.route('/action/ramasser', methods=['POST'])
def api_rammassage(request, pin_aimant=MoteurPAP, pin_ea=pin_aimant, RobotMoteurs=Robot_moteurs):
    print("Action: cycle_rammassage déclenchée via /action/ramasser")
    try:
        cycle_rammassage(pin_ea, pin_aimant, RobotMoteurs)
        return Response(json.dumps({"status": "ok", "action": "cycle_rammassage"}), headers={'Content-Type': 'application/json'})
    except Exception as e:
        print(f"Erreur lors du cycle_rammassage: {e}")
        return Response(json.dumps({"status": "error", "message": str(e)}), headers={'Content-Type': 'application/json'}, status_code=500)

@app.route('/api/distance_obstacle/', methods=['GET'])
def get_ip_raspberry(request, capteur = capteur_obstacle):
    return Response(json.dumps({"distance": capteur.mesure_distance() if capteur else "No Data"}), headers={'Content-Type': 'application/json'})

@app.route('/api/metal/', methods=['GET'])
def get_ip_raspberry(request, metal = metal_detected):
    print("Vérification de la présence de métal", metal)
    return Response(json.dumps({"metal": "metal" if metal else "No metal"}), headers={'Content-Type': 'application/json'})

# Ajout du middleware CORS pour autoriser les requêtes cross-origin
@app.after_request
def add_cors_headers(request, response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# --- Lancer le serveur ---
def start_server():
    try:
        print(f"Démarrage du serveur sur http://{ip_address}:80")
        if ecran_lcd:
            ecran_lcd.clear()
            ecran_lcd.putstr("Serveur: ON")
            sleep(0.5)
            ecran_lcd.clear()
            ecran_lcd.putstr(f"IP: {ip_address} : 80")
        app.run(host="0.0.0.0", port=80)
    except Exception as e:
        print(f"Erreur serveur: {e}")
        if ecran_lcd:
            ecran_lcd.clear()
            ecran_lcd.putstr("Erreur serveur")


if __name__ == "__main__":
    start_server()
