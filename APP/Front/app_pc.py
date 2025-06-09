from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import os
import requests
import serial
import json
import time
from threading import Thread

app = Flask(__name__)  # Pas de static_folder pour l'instant
CORS(app)

# --- Variables d'état globales ---
robot_state = {
    "mode": "manuel",  # manuel ou auto
    "battery": 75,     # pourcentage de batterie simulé
    "power": True      # état d'alimentation (on/off)
}

# Stockage temporaire en mémoire pour les coordonnées GPS
gps_coords = {"coords": []}
# Stockage temporaire pour la position du robot
robot_position = {"lat": None, "lng": None}

# Configuration pour communiquer avec la Raspberry Pico
PICO_IP = "" #"192.168.218.240"  # Remplacez par l'IP RÉELLE de votre Pico
PICO_PORT = 80

# Variables de communication (HTTP uniquement)
use_serial = False  # Toujours HTTP

# --- Fonction pour envoyer des commandes à la Pico ---
def send_to_pico(endpoint, data=None, method="POST"):
    """Envoie une commande à la Raspberry Pico via HTTP uniquement"""
    try:
        url = f"http://{PICO_IP}:{PICO_PORT}{endpoint}"
        print(f"Envoi vers Pico: {method} {url}")
        headers = {'Content-Type': 'application/json'}
        if method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=5)
        else:
            response = requests.get(url, headers=headers, timeout=5)
        return response.json()
    except Exception as e:
        print(f"Erreur communication avec Pico: {e}")
        return {"status": "error", "message": str(e)}

# --- Routes pour servir les fichiers statiques ---
@app.route('/')
@app.route('/index.html')
def index():
    try:
        # Cherche le fichier dans le même dossier que app_pc.py
        with open('index.html', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "Fichier index.html non trouvé dans le dossier courant", 404

@app.route('/map.html')
def map_html():
    try:
        with open('map.html', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "Fichier map.html non trouvé", 404

@app.route('/js/<filename>')
def serve_js(filename):
    try:
        with open(f'js/{filename}', 'r', encoding='utf-8') as file:
            return file.read(), 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return f"Fichier {filename} non trouvé", 404

@app.route('/css/<filename>')
def serve_css(filename):
    try:
        with open(f'css/{filename}', 'r', encoding='utf-8') as file:
            return file.read(), 200, {'Content-Type': 'text/css'}
    except FileNotFoundError:
        return f"Fichier {filename} non trouvé", 404

# --- Routes API ---
@app.route('/api/mode', methods=['GET'])
def get_mode():
    return jsonify({"mode": robot_state["mode"]})

@app.route('/api/mode/auto', methods=['POST'])
def set_auto():
    robot_state["mode"] = "auto"
    print("🤖 Mode automatique activé")
    
    # Transmettre la commande à la Pico
    pico_response = send_to_pico('/api/mode/auto')
    
    return jsonify({"status": "ok", "mode": "auto", "pico_response": pico_response})

@app.route('/api/mode/manual', methods=['POST'])
def set_manual():
    robot_state["mode"] = "manuel"
    print("🔧 Mode manuel activé")
    
    # Transmettre la commande à la Pico
    pico_response = send_to_pico('/api/mode/manual')
    
    return jsonify({"status": "ok", "mode": "manuel", "pico_response": pico_response})

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(robot_state)

# Routes de commande de mouvement
@app.route('/api/move/<direction>', methods=['POST'])
def move(direction):
    if robot_state["mode"] == "manuel" and robot_state["power"]:
        print(f"Mouvement: {direction}")
        
        # Transmettre la commande à la Pico
        pico_response = send_to_pico(f'/api/move/{direction}')
        
        return jsonify({
            "status": "ok", 
            "action": f"move_{direction}",
            "pico_response": pico_response
        })
    else:
        return jsonify({
            "status": "error", 
            "message": "Le robot ne peut pas être contrôlé manuellement dans ce mode"
        }), 400

# Route pour contrôler la vitesse (corrigée)
@app.route('/api/speed', methods=['POST'])
def set_speed():
    data = request.get_json()
    print(f"Données reçues du client: {data}")
    
    # Validation et extraction de la vitesse
    speed = 50  # valeur par défaut
    
    if data is not None:
        if "speed" in data:
            try:
                speed = int(data["speed"])
            except (ValueError, TypeError):
                speed = 50
        elif "description" in data:
            try:
                speed = int(data["description"])
            except (ValueError, TypeError):
                speed = 50
    
    # Validation de la plage de vitesse
    speed = max(0, min(100, speed))
    
    # Préparer les données pour la Pico
    payload = {"speed": speed}
    
    print(f"Vitesse validée envoyée à la Pico: {payload}")
    pico_response = send_to_pico('/api/speed', payload)
    
    return jsonify({
        "status": "ok",
        "speed": speed,
        "pico_response": pico_response
    })

# Routes d'actions du robot
@app.route('/action/ramasser', methods=['POST'])
def action_pickup():
    print("Action: Ramassage")
    
    # Transmettre la commande à la Pico
    pico_response = send_to_pico('/action/ramasser')
    
    return jsonify({
        "status": "ok", 
        "action": "ramasser",
        "pico_response": pico_response
    })

@app.route('/action/vider', methods=['POST'])
def action_empty():
    print("Action: Vider le bac")
    
    # Transmettre la commande à la Pico
    pico_response = send_to_pico('/action/vider')
    
    return jsonify({
        "status": "ok", 
        "action": "vider",
        "pico_response": pico_response
    })

@app.route('/action/retour', methods=['POST'])
def action_return():
    print("Action: Retour à la base")
    
    # Transmettre la commande à la Pico
    pico_response = send_to_pico('/action/retour')
    
    return jsonify({
        "status": "ok", 
        "action": "retour",
        "pico_response": pico_response
    })

# API pour les coordonnées GPS
@app.route('/api/coordgsp/', methods=['GET', 'POST'])
def coordgsp():
    global gps_coords
    if request.method == 'POST':
        data = request.get_json()
        if data and "coords" in data:
            gps_coords["coords"] = data["coords"]
            # Optionnel: transmettre à la Pico
            send_to_pico('/api/coordgps/', data)
        return jsonify({"status": "ok"})
    else:
        return jsonify(gps_coords)

# API pour la position du robot
@app.route('/api/coordrobot/', methods=['GET', 'POST'])
def coordrobot():
    global robot_position
    if request.method == 'POST':
        data = request.get_json()
        if data and "lat" in data and "lng" in data:
            robot_position["lat"] = data["lat"]
            robot_position["lng"] = data["lng"]
            # Optionnel: transmettre à la Pico
            send_to_pico('/api/coordrobot/', data)
            return jsonify({"status": "ok"})
        return jsonify({"status": "error", "message": "lat/lng manquants"}), 400
    else:
        # Récupérer la position depuis la Pico
        pico_response = send_to_pico('/api/coordrobot/', method="GET")
        if pico_response.get("status") != "error":
            robot_position.update(pico_response)
        return jsonify(robot_position)

# Route pour tester la communication avec la Pico
@app.route('/api/test-pico', methods=['GET'])
def test_pico():
    response = send_to_pico('/api/status', method="GET")
    return jsonify({
        "pc_status": "ok",
        "pico_response": response,
        "communication_method": "serial" if use_serial else "http"
    })

# --- Route pour modifier dynamiquement l'IP de la Pico ---
@app.route('/api/set_pico_ip', methods=['POST'])
def set_pico_ip():
    global PICO_IP
    data = request.get_json()
    if not data or 'ip' not in data:
        return jsonify({'status': 'error', 'message': 'IP manquante'}), 400
    ip = data['ip']
    # Validation simple de l'IP
    import re
    if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip):
        return jsonify({'status': 'error', 'message': 'Format IP invalide'}), 400
    PICO_IP = ip
    print(f"Nouvelle IP Pico enregistrée: {PICO_IP}")
    return jsonify({'status': 'ok', 'ip': PICO_IP})

# Fonction pour maintenir la synchronisation avec la Pico
def sync_with_pico():
    """Thread pour synchroniser périodiquement l'état avec la Pico"""
    while True:
        try:
            pico_status = send_to_pico('/api/status', method="GET")
            if pico_status.get("status") != "error":
                # Mettre à jour l'état local avec les données de la Pico
                for key in ["mode", "battery", "power"]:
                    if key in pico_status:
                        robot_state[key] = pico_status[key]
        except Exception as e:
            print(f"Erreur synchronisation: {e}")
        time.sleep(5)  # Synchroniser toutes les 5 secondes

if __name__ == '__main__':
    print("Serveur Flask démarré sur http://0.0.0.0:5000")
    print("Configuration:")
    print(f"  - Communication: HTTP uniquement")
    print(f"  - Pico IP: {PICO_IP}")
    print("\nPour tester:")
    print("  1. Mettez vos fichiers HTML/CSS/JS dans le même dossier que app_pc.py")
    print("  2. Changez PICO_IP par l'IP réelle de votre Pico")
    print("  3. Accédez depuis votre téléphone à: http://IP_DE_VOTRE_PC:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)