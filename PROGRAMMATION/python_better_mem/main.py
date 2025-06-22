from microdot import Microdot, Response, Request
from machine import Pin 
from time import sleep, ticks_ms, ticks_diff
import json
import gc
from connection_pico_wifi import connect_wifi, test_internet
from deplacements import RobotMoteurs, MoteurPasAPas
from cycle_rammassage import cycle_rammassage
from depart_ok import depart_ok
from utils import is_point_in_polygon, find_closest_point_polygon, calculate_cap
from cycle_evite_obstacle import cycle_evitement
from vider_benne import ServoBenne, cycle_vider_bac

# Force la collection garbage au démarrage
gc.collect()
print(f"MEMOIRE INITIALE: {gc.mem_free()}")


# Configuration garbage collector plus agressive
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

capteur_gps, ecran_lcd, capteur_compas, capteur_obstacle = depart_ok()

gc.collect()
Robot_moteurs = RobotMoteurs()
MoteurPAP = MoteurPasAPas()
pin_aimant = Pin(20, Pin.OUT)

# Initialisation données avec moins d'allocations
polygone = []
gps_coords = []
robot_speed = 50
robot_position = [None, None]  # liste au lieu de dict pour économiser mémoire

# Connexion Wi-Fi
print(f"[DEBUG] Mémoire avant WiFi: {gc.mem_free()}")
ip_address = connect_wifi(ssid="OnePlus 6", password="12345678", LCD=ecran_lcd)
gc.collect()
print(f"[DEBUG] Mémoire après WiFi: {gc.mem_free()}")

# Application Web
app = Microdot()
Response.default_content_type = 'text/html'

# Variables d'état optimisées
robot_state = ["manuel", 75, True]  # [mode, battery, power] - liste au lieu de dict

# Pins
METAL_DETECTOR_PIN = 26
BUTTON_PIN = 22
metal_detected = False
mode_auto_active = False

button_pin = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
last_button_state = 1
last_button_time = 0

print(f"[DEBUG] Mémoire après init: {gc.mem_free()}")

# Fonction utilitaire pour créer des réponses JSON optimisées
def create_json_response(data, status=200):
    """Créer une réponse JSON et libérer immédiatement la mémoire"""
    json_str = json.dumps(data)
    del data  # Libère immédiatement le dict
    gc.collect()
    return Response(json_str, status, {'Content-Type': 'application/json'})

# Routes API optimisées
@app.route('/api/mode', methods=['GET'])
def get_mode(request):
    gc.collect()  # Nettoyage avant traitement
    data = {"mode": robot_state[0]}
    return create_json_response(data)

@app.route('/api/mode/auto', methods=['POST'])
def set_auto(request):
    robot_state[0] = "auto"
    print("Mode automatique activé")
    if ecran_lcd:
        ecran_lcd.clear()
        ecran_lcd.putstr("Mode: AUTO")
    
    gc.collect()
    
    if robot_state[0] == "auto":
        print("Démarrage du mode automatique")
        main_auto(CapteurGps=capteur_gps, 
                  EcranLCD=ecran_lcd, 
                  Compas=capteur_compas, 
                  CapteurObstacle=capteur_obstacle, 
                  polygone=polygone, 
                  RobotMoteurs=Robot_moteurs, 
                  MoteurPAP=MoteurPAP, 
                  pin_aimant=pin_aimant)
        gc.collect()
    
    data = {"status": "ok", "mode": "auto"}
    return create_json_response(data)

@app.route('/api/mode/manual', methods=['POST'])
def set_manual(request):
    robot_state[0] = "manuel"
    print("🔧 Mode manuel activé")
    if ecran_lcd:
        ecran_lcd.clear()
        ecran_lcd.putstr("Mode: MANUEL")
    
    data = {"status": "ok", "mode": "manuel"}
    return create_json_response(data)

@app.route('/api/status', methods=['GET'])
def get_status(request):
    gc.collect()
    data = {"mode": robot_state[0], "battery": robot_state[1], "power": robot_state[2]}
    return create_json_response(data)

@app.route('/api/move/<direction>', methods=['POST'])
def move(request, direction):
    gc.collect()  # Nettoyage avant traitement
    print(f"MEMOIRE AVANT MOVE: {gc.mem_free()}")
    
    if robot_state[0] == "manuel" and robot_state[2]:
        Robot_moteurs.vitesse(60000)
        
        # Dictionnaire local pour éviter les allocations répétées
        if direction == "forward":
            Robot_moteurs.avancer()
            action = "avancer"
        elif direction == "backward":
            Robot_moteurs.reculer()
            action = "reculer"
        elif direction == "left":
            Robot_moteurs.gauche()
            action = "gauche"
        elif direction == "right":
            Robot_moteurs.droite()
            action = "droite"
        elif direction == "stop":
            Robot_moteurs.stop()
            action = "stop"
        else:
            action = "unknown"
            
        print(f"Mouvement: {direction} {action}")
        
        if ecran_lcd:
            ecran_lcd.clear()
            ecran_lcd.putstr(direction)
        
        data = {"status": "ok", "action": f"move_{direction}"}
        gc.collect()  # Nettoyage après traitement
        print(f"MEMOIRE APRÈS MOVE: {gc.mem_free()}")
        return create_json_response(data)
    else:
        data = {"status": "error", "message": "Mode incorrect"}
        return create_json_response(data, 400)

@app.route('/api/coordrobot/', methods=['GET', 'POST'])
def coordrobot(request):
    gc.collect()
    global robot_position
    
    if request.method == 'POST':
        try:
            data = request.json
            if data and "lat" in data and "lng" in data:
                robot_position[0] = data["lat"]
                robot_position[1] = data["lng"]
                del data  # Libère immédiatement
                gc.collect()
                response_data = {"status": "ok"}
                return create_json_response(response_data)
            else:
                response_data = {"status": "error", "message": "lat/lng manquants"}
                return create_json_response(response_data, 400)
        except Exception as e:
            response_data = {"status": "error", "message": "JSON invalide"}
            return create_json_response(response_data, 400)
    else:
        # GET - mise à jour position GPS
        try:
            if capteur_gps:
                coords = capteur_gps.read()
                if coords:
                    robot_position[0] = coords[1]  # lat
                    robot_position[1] = coords[0]  # lng
                else:
                    robot_position[0] = None
                    robot_position[1] = None
        except Exception:
            robot_position[0] = None
            robot_position[1] = None
        
        response_data = {"lat": robot_position[0], "lng": robot_position[1]}
        return create_json_response(response_data)

@app.route('/api/coordgps/', methods=['GET', 'POST'])
def coordgsp(request):
    gc.collect()
    global gps_coords, polygone
    
    if request.method == 'POST':
        try:
            data = request.json
            if data and "coords" in data:   
                gps_coords = data["coords"]
                polygone = gps_coords
                print("Polygone mis à jour:", len(polygone), "points")
                del data  # Libère immédiatement
                gc.collect()
                
                if ecran_lcd:
                    ecran_lcd.clear()
                    ecran_lcd.putstr("Polygone OK")
                
                response_data = {"status": "ok"}
                return create_json_response(response_data)
            else:
                response_data = {"status": "error", "message": "coords manquants"}
                return create_json_response(response_data, 400)
        except Exception as e:
            response_data = {"status": "error", "message": "Erreur JSON"}
            return create_json_response(response_data, 400)
    else:
        response_data = {"coords": gps_coords}
        return create_json_response(response_data)

@app.route('/api/speed', methods=['POST', 'GET'])
def set_speed(request):
    gc.collect()
    global robot_speed
    
    if request.method == 'POST':
        try:
            data = request.json
            speed = None
            
            if data:
                speed = data.get('speed') or data.get('description')
            
            if speed is None:
                speed = 50
            
            del data  # Libère immédiatement
            gc.collect()
            
            # Conversion PWM
            pwm_value = int((int(speed) / 100) * 65000)
            Robot_moteurs.vitesse(pwm_value)
            robot_speed = int(speed)
            
            print(f"Vitesse: {speed}% (PWM={pwm_value})")
            
            if ecran_lcd:
                ecran_lcd.clear()
                ecran_lcd.putstr(f"Vitesse: {speed}%")
            
            response_data = {"status": "ok", "speed": speed}
            return create_json_response(response_data)
            
        except Exception as e:
            response_data = {"status": "error", "message": "Erreur vitesse"}
            return create_json_response(response_data, 400)
    else:
        response_data = {"speed": robot_speed}
        return create_json_response(response_data)

@app.route('/action/ramasser', methods=['POST'])
def api_rammassage(request):
    gc.collect()
    print("Action: cycle_rammassage")
    try:
        cycle_rammassage(pin_aimant, MoteurPAP, Robot_moteurs)
        gc.collect()
        response_data = {"status": "ok", "action": "cycle_rammassage"}
        return create_json_response(response_data)
    except Exception as e:
        print(f"Erreur ramassage: {e}")
        response_data = {"status": "error", "message": str(e)}
        return create_json_response(response_data, 500)

@app.route('/api/distance_obstacle/', methods=['GET'])
def get_distance_obstacle(request):
    gc.collect()
    distance = capteur_obstacle.mesure_distance() if capteur_obstacle else "No Data"
    response_data = {"distance": distance}
    return create_json_response(response_data)

@app.route('/action/vider', methods=['POST', 'GET'])
def vider_benne(request):
    servo_benne = ServoBenne(pin=28)
    gc.collect()
    ecran_lcd.clear()
    ecran_lcd.putstr("Vider benne...")
    cycle_vider_bac(servo_benne)
    ecran_lcd.clear()
    ecran_lcd.putstr("Benne videe")
    response_data = {"status": "ok"}
    del servo_benne
    gc.collect()  # Nettoyage mémoire après l'action
    return create_json_response(response_data)

@app.route('/api/metal/', methods=['GET'])
def get_metal_status(request):
    gc.collect()
    global metal_detected
    handle_metal_detection()  # Met à jour l'état avant de répondre
    response_data = {"metal": "metal" if metal_detected else "No metal"}
    return create_json_response(response_data)

# Middleware CORS optimisé
@app.after_request
def add_cors_headers(request, response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    gc.collect()  # Nettoyage après chaque requête
    return response


############################################################################################################
# Fonction pour gérer la détection de métal sans thread
metal_timer = 0
def handle_metal_detection():
    global metal_detected, metal_timer
    if metal_detected and ticks_diff(ticks_ms(), metal_timer) > 5000:  # 10s
        metal_detected = False
        print("Fin affichage détection métal")

# Callback optimisé pour détection métal
def metal_detection_callback(pin):
    global metal_detected, mode_auto_active, metal_timer
    if mode_auto_active:
        metal_detected = True
        print("Métal détecté! (auto)")
    else:
        if not metal_detected:
            metal_detected = True
            metal_timer = ticks_ms()
            print("Métal détecté! (manuel)")

# Configuration détecteur métal
detector_pin = Pin(METAL_DETECTOR_PIN, Pin.IN)
detector_pin.irq(trigger=Pin.IRQ_RISING, handler=metal_detection_callback)

# Fonction de ramassage optimisée
def collect_metal(MoteurPAP, RobotMoteurs, pin_aimant):
    print("Cycle de ramassage")
    try:
        ramassage = cycle_rammassage(pin_EA=pin_aimant, MoteurPAP=MoteurPAP, RobotMoteurs=RobotMoteurs)
        gc.collect()
        sleep(1)
        return ramassage
    except Exception as e:
        print(f"Erreur ramassage: {e}")
        return False

# Fonction main_auto optimisée
def main_auto(CapteurGps, EcranLCD, Compas, CapteurObstacle, polygone, RobotMoteurs, MoteurPAP, pin_aimant):
    global metal_detected, mode_auto_active
    mode_auto_active = True
    
    if not all([CapteurGps, EcranLCD, Compas, CapteurObstacle, RobotMoteurs, MoteurPAP]):
        print("Capteurs manquants")
        last_button_state = 1
        last_button_time = ticks_ms()
        
        while True:
            button_state = button_pin.value()
            now = ticks_ms()
            if last_button_state == 1 and button_state == 0 and ticks_diff(now, last_button_time) > 300:
                print("Sortie mode auto (capteurs manquants)")
                mode_auto_active = False
                return
            last_button_state = button_state
            
            if metal_detected:
                print("Métal détecté, impossible de ramasser")
                sleep(2)
                metal_detected = False
                
            if EcranLCD:
                EcranLCD.clear()
                EcranLCD.putstr("Erreur capteurs")
            
            # Nettoyage périodique
            gc.collect()
            sleep(1)
    
    print("Démarrage robot mode auto")
    last_button_state = 1
    last_button_time = ticks_ms()
    
    while True:
        # Gestion bouton physique
        button_state = button_pin.value()
        now = ticks_ms()
        if last_button_state == 1 and button_state == 0 and ticks_diff(now, last_button_time) > 300:
            print("Sortie mode auto")
            mode_auto_active = False
            return
        last_button_state = button_state

        # Détection métal
        if metal_detected:
            collect_metal(MoteurPAP=MoteurPAP, RobotMoteurs=RobotMoteurs, pin_aimant=pin_aimant)
            metal_detected = False
        
        # Nettoyage périodique en mode auto
        gc.collect()
        
        try:
            longitude, latitude = CapteurGps.read()
            distance = CapteurObstacle.mesure_distance()
            
            if distance and distance < 10:
                print("Obstacle détecté")
                cycle_evitement(CapteurObstacle, RobotMoteurs)
                gc.collect()
            
            if polygone and longitude and latitude:
                inside = is_point_in_polygon(lat=latitude, lon=longitude, polygon=polygone)
                
                if not inside:
                    print("Hors polygone")
                    closest_point = find_closest_point_polygon(latitude, longitude, polygone)
                    cap_retour = calculate_cap(latitude, longitude, closest_point[0], closest_point[1])
                    
                    cap_actuel = Compas.lire_cap()
                    if cap_actuel is not None:
                        diff = (cap_retour - cap_actuel + 540) % 360 - 180
                        seuil_alignement = 10
                        
                        if abs(diff) <= seuil_alignement:
                            RobotMoteurs.avancer()
                        elif diff > 0:
                            RobotMoteurs.gauche()
                        else:
                            RobotMoteurs.droite()
                    else:
                        RobotMoteurs.stop()
                else:
                    RobotMoteurs.avancer()
            else:
                RobotMoteurs.avancer()
                
        except Exception as e:
            print(f"Erreur boucle auto: {e}")
            RobotMoteurs.stop()
        
        # Gestion détection métal en mode manuel
        handle_metal_detection()
        
        sleep(0.5)

# Fonction serveur
def start_server():
    try:
        print(f"Serveur sur http://{ip_address}:80")
        if ecran_lcd:
            ecran_lcd.clear()
            ecran_lcd.putstr("Serveur: ON")
            sleep(0.5)
            ecran_lcd.clear()
            ecran_lcd.putstr(f"IP: {ip_address}")
        
        # Nettoyage final avant démarrage serveur
        gc.collect()
        print(f"Mémoire disponible au démarrage serveur: {gc.mem_free()}")
        
        app.run(host="0.0.0.0", port=80)
    except Exception as e:
        print(f"Erreur serveur: {e}")
        if ecran_lcd:
            ecran_lcd.clear()
            ecran_lcd.putstr("Erreur serveur")

if __name__ == "__main__":
    start_server()