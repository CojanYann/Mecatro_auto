from microdot import Microdot, Response, Request
from machine import I2C, Pin
import network
import machine
import time
import json
import socket
import gc
from lecture_lcd import LCD
from connection_pico_wifi import connect_wifi, test_internet
from deplacements import RobotMoteurs, MoteurPasAPas
from cycle_rammassage import cycle_rammassage

# init capteurs

LCD = LCD()
RobotMoteurs = RobotMoteurs()

MoteurPAP = MoteurPasAPas()
pin_aimant = Pin(20, Pin.OUT)

# --- Connexion Wi-Fi ---

ip_address = connect_wifi(ssid="OnePlus 6", password="12345678", LCD=LCD)
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
    print("test depart")
    # Initialisation des capteurs en mode local, pas global

    print("Mémoire libérée après initialisation des capteurs")
    # Ici vous ajouteriez le code pour le comportement autonome
    # Par exemple, la détection et le ramassage de déchets


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
def move(request, direction, RobotMoteurs=RobotMoteurs, LCD=LCD):
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
    
gps_coords = {"coords": []}

@app.route('/api/coordgps/', methods=['GET', 'POST'])
def coordgsp(request):
    global gps_coords
    if request.method == 'POST':
        data = request.json
        if data and "coords" in data:
            gps_coords["coords"] = data["coords"]
        return Response(json.dumps({"status": "ok"}), headers={'Content-Type': 'application/json'})
    else:
        return Response(json.dumps(gps_coords), headers={'Content-Type': 'application/json'})

@app.route('/api/speed', methods=['POST'])
def set_speed(request, RobotMoteurs=RobotMoteurs, LCD=LCD):
    # Utilise get_json() pour parser le JSON de façon robuste
    try:
        data = request.get_json()
    except Exception:
        data = None
    print(data, "ou rien")
    # Accepte à la fois {"speed": 65} ou {"description": 65}
    speed = None
    if data:
        if 'speed' in data:
            speed = data['speed']
        elif 'description' in data:
            speed = data['description']
    if speed is None:
        speed = 50  # valeur par défaut
    # Conversion de la vitesse en valeur PWM (0-65535)
    pwm_value = int((int(speed) / 100) * 65535)
    RobotMoteurs.vitesse(pwm_value)
    print(f"Vitesse réglée à: {speed}% (PWM={pwm_value})")
    if LCD:
        LCD.clear()
        LCD.putstr(f"Vitesse: {speed}%")
    return Response(json.dumps({"status": "ok", "speed": speed}), headers={'Content-Type': 'application/json'})

@app.route('/action/ramasser', methods=['POST'])
def api_rammassage(request, pin_aimant=MoteurPAP, pin_ea=pin_aimant, RobotMoteurs=RobotMoteurs):
    print("Action: cycle_rammassage déclenchée via /action/ramasser")
    try:
        cycle_rammassage(pin_ea, pin_aimant, RobotMoteurs)
        return Response(json.dumps({"status": "ok", "action": "cycle_rammassage"}), headers={'Content-Type': 'application/json'})
    except Exception as e:
        print(f"Erreur lors du cycle_rammassage: {e}")
        return Response(json.dumps({"status": "error", "message": str(e)}), headers={'Content-Type': 'application/json'}, status_code=500)

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
