from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='../Front')
CORS(app)

# Stockage temporaire en mémoire pour les coordonnées GPS
gps_coords = {"coords": []}
# Stockage temporaire pour la position du robot
robot_position = {"lat": None, "lng": None}

# Routes pour servir les fichiers statiques
@app.route('/index.html')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/map.html')
def map_html():
    return send_from_directory(app.static_folder, 'map.html')

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(app.static_folder, 'js'), filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(app.static_folder, 'css'), filename)

# API pour les coordonnées GPS
@app.route('/api/coordgsp/', methods=['GET', 'POST'])
def coordgsp():
    global gps_coords
    if request.method == 'POST':
        data = request.get_json()
        if data and "coords" in data:
            gps_coords["coords"] = data["coords"]
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
            return jsonify({"status": "ok"})
        return jsonify({"status": "error", "message": "lat/lng manquants"}), 400
    else:
        return jsonify(robot_position)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
