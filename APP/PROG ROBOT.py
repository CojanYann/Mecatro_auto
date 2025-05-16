import network
import machine
import time
import uasyncio as asyncio
from machine import Pin, PWM, I2C, UART
import binascii
import hashlib
import ujson as json
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
from bmm150 import BMM150

# Configuration Wi-Fi
SSID = "iPhone de Yoann"
PASSWORD = "yoann2003"

# Configuration LCD
LCD_I2C_ID = 0
LCD_I2C_SCL_PIN = 17
LCD_I2C_SDA_PIN = 16
LCD_I2C_FREQ = 400000
LCD_ADDR = 0x27  # Adresse I2C standard pour SBC-LCD16x2, à ajuster si nécessaire
LCD_COLS = 16
LCD_ROWS = 2

# Configuration du compas numérique BMM150
COMPASS_I2C_ID = 1
COMPASS_I2C_SCL_PIN = 3
COMPASS_I2C_SDA_PIN = 2

# Configuration GPS Air530
GPS_UART_ID = 0
GPS_UART_TX_PIN = 0
GPS_UART_RX_PIN = 1
GPS_BAUD_RATE = 9600

# Configuration du servomoteur
SERVO_PIN = 13
FREQ = 50

# Configuration des capteurs à ultrasons HC-SR04
TRIGGER_PIN1 = 15
ECHO_PIN1 = 14
TRIGGER_PIN2 = 19
ECHO_PIN2 = 18

# Initialisation des broches pour les capteurs à ultrasons
trigger1 = Pin(TRIGGER_PIN1, Pin.OUT)
echo1 = Pin(ECHO_PIN1, Pin.IN)
trigger2 = Pin(TRIGGER_PIN2, Pin.OUT)
echo2 = Pin(ECHO_PIN2, Pin.IN)

# Variables globales pour stocker les dernières mesures
last_distance1 = 0
last_distance2 = 0
current_latitude = 0.0
current_longitude = 0.0
current_heading = 0
gps_time = "07:47:29"
gps_date = "2025-05-16"  # Date actuelle

# Initialisation des périphériques
servo = PWM(Pin(SERVO_PIN))
servo.freq(FREQ)

# Initialisation du LCD
i2c_lcd = I2C(LCD_I2C_ID, 
              scl=Pin(LCD_I2C_SCL_PIN),
              sda=Pin(LCD_I2C_SDA_PIN),
              freq=LCD_I2C_FREQ)

lcd = None
try:
    lcd_devices = i2c_lcd.scan()
    if lcd_devices:
        print(f"Périphériques I2C détectés: {lcd_devices}")
        LCD_ADDR = lcd_devices[0]  # Utiliser la première adresse trouvée
    lcd = I2cLcd(i2c_lcd, LCD_ADDR, LCD_ROWS, LCD_COLS)
    print("LCD initialisé avec succès")
except Exception as e:
    print(f"Erreur lors de l'initialisation du LCD: {e}")
    lcd = None

# Initialisation du compas BMM150
compass = None
try:
    i2c_compass = I2C(COMPASS_I2C_ID,
                    scl=Pin(COMPASS_I2C_SCL_PIN),
                    sda=Pin(COMPASS_I2C_SDA_PIN),
                    freq=400000)
    
    compass_devices = i2c_compass.scan()
    if compass_devices:
        print(f"Périphériques I2C compas détectés: {compass_devices}")
        compass = BMM150(i2c_compass, addr=compass_devices[0])
        print("Compas BMM150 initialisé avec succès")
    else:
        print("Aucun périphérique I2C trouvé pour le compas")
except Exception as e:
    print(f"Erreur lors de l'initialisation du compas: {e}")
    compass = None

# Initialisation du GPS
gps_uart = UART(GPS_UART_ID,
                baudrate=GPS_BAUD_RATE,
                tx=Pin(GPS_UART_TX_PIN),
                rx=Pin(GPS_UART_RX_PIN))

print("GPS UART initialisé")

def set_servo_angle(angle):
    duty = int(2040 + (angle * 10.5))
    servo.duty_u16(duty)
    print(f"Servo défini à {angle}°")

# Code simplifié pour HC-SR04
def measure_distance(trigger, echo):
    """
    Fonction simplifiée pour mesurer la distance avec un capteur HC-SR04
    """
    # Envoi de l'impulsion
    trigger.value(0)
    time.sleep_us(5)
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)
    
    # Attente du début de l'écho
    while echo.value() == 0:
        pulse_start = time.ticks_us()
    
    # Attente de la fin de l'écho
    while echo.value() == 1:
        pulse_end = time.ticks_us()
    
    # Calcul de la distance
    pulse_duration = time.ticks_diff(pulse_end, pulse_start)
    distance_cm = pulse_duration * 0.0343 / 2
    
    return round(distance_cm, 1)

def parse_gps_data(data):
    global current_latitude, current_longitude, gps_time, gps_date
    
    # Vérifier si c'est une phrase NMEA valide
    if data.startswith(b"$"):
        try:
            # Convertir bytes en string
            data_str = data.decode('ascii').strip()
            parts = data_str.split(',')
            
            # Traiter les données GPS selon le type de phrase NMEA
            if data_str.startswith("$GPRMC") and len(parts) >= 10:
                # Format: $GPRMC,time,status,lat,N/S,lon,E/W,speed,course,date,...
                if parts[2] == 'A':  # A = données valides, V = non valides
                    # Extraire l'heure (format HHMMSS.sss)
                    time_str = parts[1]
                    if time_str:
                        hour = time_str[0:2]
                        minute = time_str[2:4]
                        second = time_str[4:6]
                        gps_time = f"{hour}:{minute}:{second}"
                    
                    # Extraire la date (format DDMMYY)
                    date_str = parts[9]
                    if date_str:
                        day = date_str[0:2]
                        month = date_str[2:4]
                        year = f"20{date_str[4:6]}"  # Ajouter le préfixe '20' car on est au 21e siècle
                        gps_date = f"{year}-{month}-{day}"
                    
                    # Extraire et convertir la latitude
                    lat = parts[3]
                    lat_dir = parts[4]  # N ou S
                    if lat and lat_dir:
                        try:
                            lat_deg = float(lat[0:2])
                            lat_min = float(lat[2:])
                            latitude = lat_deg + (lat_min / 60.0)
                            if lat_dir == 'S':
                                latitude = -latitude
                            current_latitude = round(latitude, 6)
                        except ValueError:
                            pass
                    
                    # Extraire et convertir la longitude
                    lon = parts[5]
                    lon_dir = parts[6]  # E ou W
                    if lon and lon_dir:
                        try:
                            lon_deg = float(lon[0:3])
                            lon_min = float(lon[3:])
                            longitude = lon_deg + (lon_min / 60.0)
                            if lon_dir == 'W':
                                longitude = -longitude
                            current_longitude = round(longitude, 6)
                        except ValueError:
                            pass
            
            return True
        except Exception as e:
            print(f"Erreur lors du parsing GPS: {e}")
            return False
    
    return False

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("Connexion au Wi-Fi...")
    wlan.connect(SSID, PASSWORD)
    
    max_retries = 10
    retries = 0
    while not wlan.isconnected() and retries < max_retries:
        print("Tentative de connexion...")
        retries += 1
        time.sleep(1)
    
    if wlan.isconnected():
        ifconfig = wlan.ifconfig()
        print("Connecté au Wi-Fi!")
        print(f"Adresse IP: {ifconfig[0]}")
        return ifconfig[0]
    else:
        raise RuntimeError("Impossible de se connecter au Wi-Fi.")

def update_lcd():
    global current_latitude, current_longitude, current_heading
    
    if lcd is None:
        return
        
    try:
        lcd.clear()
        
        # Formatage des coordonnées GPS pour l'affichage LCD
        lat_str = f"Lat:{current_latitude:.5f}"
        
        # Affichage des coordonnées GPS sur la première ligne (côté gauche)
        lcd.move_to(0, 0)
        lcd.putstr(lat_str[:8])  # Limiter à 8 caractères pour la première ligne
        
        # Affichage de l'angle du compas sur la première ligne (côté droit)
        heading_str = f"Head:{current_heading:03d}"
        lcd.move_to(8, 0)  # Positionner le curseur à la moitié de l'écran
        lcd.putstr(heading_str)
        
        # Deuxième ligne: longitude et heure GPS
        lon_str = f"Lon:{current_longitude:.5f}"
        lcd.move_to(0, 1)
        lcd.putstr(lon_str[:8])  # Longitude limitée à 8 caractères
        
        # Afficher l'heure GPS sur la deuxième ligne (côté droit)
        time_str = gps_time[:8]
        lcd.move_to(8, 1)
        lcd.putstr(time_str)
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour de l'écran LCD: {e}")

# Fonction pour créer et envoyer une trame WebSocket
def create_websocket_frame(data):
    frame = bytearray()
    frame.append(0x81)  # FIN + opcode text
    
    data_bytes = data.encode()
    length = len(data_bytes)
    
    if length < 126:
        frame.append(length)
    elif length < 65536:
        frame.append(126)
        frame.extend(length.to_bytes(2, 'big'))
    else:
        frame.append(127)
        frame.extend(length.to_bytes(8, 'big'))
    
    frame.extend(data_bytes)
    return frame

# Tâche asynchrone pour les capteurs
async def sensor_task(clients):
    global last_distance1, last_distance2, current_heading
    
    while True:
        try:
            # Mesure capteur 1 - code simplifié avec gestion des erreurs
            try:
                distance1 = measure_distance(trigger1, echo1)
                last_distance1 = distance1
                print(f"Distance 1: {distance1} cm")
            except Exception as e:
                print(f"Erreur capteur 1: {e}")
            
            # Mesure capteur 2 - code simplifié avec gestion des erreurs
            try:
                distance2 = measure_distance(trigger2, echo2)
                last_distance2 = distance2
                print(f"Distance 2: {distance2} cm")
            except Exception as e:
                print(f"Erreur capteur 2: {e}")
            
            # Lire les données du compas numérique
            if compass:
                try:
                    data = compass.read_data()
                    x = data['x']
                    y = data['y']
                    
                    # Calculer l'angle de la boussole (0-360°)
                    import math
                    heading = (180 * (1 + math.atan2(y, x) / math.pi)) % 360
                    current_heading = int(heading)
                    print(f"Compas: {current_heading}°")
                except Exception as e:
                    print(f"Erreur de lecture du compas: {e}")
            
        except Exception as e:
            print(f"Erreur générale dans la tâche capteur: {e}")
        
        # Attendre avant la prochaine mesure
        await asyncio.sleep(0.5)  # Mesure toutes les 500 ms

# Tâche asynchrone pour lire les données GPS
async def gps_task():
    buffer = bytearray(1024)
    buffer_pos = 0
    
    while True:
        if gps_uart.any():
            bytes_read = gps_uart.read(1)
            if bytes_read is not None:
                byte = bytes_read[0]
                
                if byte == ord(b'\r') or byte == ord(b'\n'):
                    if buffer_pos > 0:
                        line = buffer[:buffer_pos]
                        if parse_gps_data(line):
                            print(f"GPS: Lat:{current_latitude}, Lon:{current_longitude}, Time:{gps_time}")
                        buffer_pos = 0
                elif buffer_pos < len(buffer) - 1:
                    buffer[buffer_pos] = byte
                    buffer_pos += 1
        
        await asyncio.sleep(0.1)

# Tâche asynchrone pour mettre à jour l'écran LCD
async def lcd_update_task():
    while True:
        update_lcd()
        await asyncio.sleep(1)  # Mettre à jour l'écran toutes les secondes

# Tâche asynchrone pour envoyer des données WebSocket à intervalles réguliers
async def websocket_update_task(clients):
    while True:
        try:
            if clients:
                # Préparer les données à envoyer
                data = {
                    "type": "sensor_update",
                    "timestamp": f"{gps_date} {gps_time}",
                    "distances": {
                        "sensor1": last_distance1,
                        "sensor2": last_distance2
                    },
                    "location": {
                        "latitude": current_latitude,
                        "longitude": current_longitude
                    },
                    "compass": {
                        "heading": current_heading
                    }
                }
                
                # Convertir en JSON et envoyer
                message = json.dumps(data)
                frame = create_websocket_frame(message)
                
                for client_writer in clients:
                    try:
                        client_writer.write(frame)
                        await client_writer.drain()
                    except Exception as e:
                        print(f"Erreur envoi WebSocket: {e}")
            
        except Exception as e:
            print(f"Erreur mise à jour WebSocket: {e}")
        
        # Attendre 5 secondes comme demandé
        await asyncio.sleep(5)

# Implémentation simple de WebSocket
async def websocket_handler(reader, writer, clients):
    client_info = writer.get_extra_info('peername')
    print(f"Nouvelle connexion de {client_info}")
    
    try:
        # Lire et traiter la requête de handshake WebSocket
        request = await reader.read(1024)
        if not request:
            return
        
        request = request.decode()
        
        if "Upgrade: websocket" not in request:
            print("Pas une requête WebSocket")
            writer.write(b"HTTP/1.1 400 Bad Request\r\n\r\nPas une requête WebSocket")
            await writer.drain()
            return
        
        # Extraire la clé WebSocket
        key = None
        for line in request.split('\r\n'):
            if "Sec-WebSocket-Key:" in line:
                key = line.split(': ')[1].strip()
                break
        
        if not key:
            print("Pas de clé WebSocket")
            writer.write(b"HTTP/1.1 400 Bad Request\r\n\r\nPas de clé WebSocket")
            await writer.drain()
            return
        
        # Calculer l'en-tête Sec-WebSocket-Accept
        magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        result_string = key + magic_string
        hash_obj = hashlib.sha1(result_string.encode())
        accept = binascii.b2a_base64(hash_obj.digest())[:-1].decode()
        
        # Envoyer la réponse de handshake
        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
        )
        writer.write(response.encode())
        await writer.drain()
        
        print(f"Handshake WebSocket réussi avec {client_info}")
        
        # Ajouter client à la liste des clients connectés
        clients.append(writer)
        
        # Envoyer les données actuelles au client qui vient de se connecter
        initial_data = {
            "type": "initial_data",
            "timestamp": f"{gps_date} {gps_time}",
            "distances": {
                "sensor1": last_distance1,
                "sensor2": last_distance2
            },
            "location": {
                "latitude": current_latitude,
                "longitude": current_longitude
            },
            "compass": {
                "heading": current_heading
            }
        }
        
        initial_message = json.dumps(initial_data)
        writer.write(create_websocket_frame(initial_message))
        await writer.drain()
        
        # Boucle de traitement des trames WebSocket
        while True:
            # Lire l'en-tête de la trame WebSocket
            header = await reader.read(2)
            if not header:
                break
            
            # Décodage simple des trames WebSocket
            opcode = header[0] & 0x0F
            mask = header[1] & 0x80
            payload_len = header[1] & 0x7F
            
            # Gestion des différentes longueurs de charge utile
            if payload_len == 126:
                payload_len = int.from_bytes(await reader.read(2), 'big')
            elif payload_len == 127:
                payload_len = int.from_bytes(await reader.read(8), 'big')
            
            # Masques
            masks = await reader.read(4) if mask else None
            
            # Lire la charge utile
            data = await reader.read(payload_len)
            if mask:
                unmasked_data = bytearray(payload_len)
                for i in range(payload_len):
                    unmasked_data[i] = data[i] ^ masks[i % 4]
                data = unmasked_data
            
            # Traiter les différents opcodes
            if opcode == 0x1:  # Trame texte
                message = data.decode('utf-8')
                print(f"Message reçu de {client_info}: {message}")
                
                # Traitement du message
                if message.lower() == "getdata":
                    # Envoyer toutes les données actuelles
                    current_data = {
                        "type": "data_request",
                        "timestamp": f"{gps_date} {gps_time}",
                        "distances": {
                            "sensor1": last_distance1,
                            "sensor2": last_distance2
                        },
                        "location": {
                            "latitude": current_latitude,
                            "longitude": current_longitude
                        },
                        "compass": {
                            "heading": current_heading
                        }
                    }
                    response = json.dumps(current_data)
                else:
                    # Traiter comme une commande de servo
                    try:
                        angle = int(message)
                        if 0 <= angle <= 180:
                            set_servo_angle(angle)
                            response = json.dumps({
                                "type": "servo",
                                "message": f"Angle défini à {angle}°"
                            })
                        else:
                            response = json.dumps({
                                "type": "error",
                                "message": "L'angle doit être entre 0 et 180."
                            })
                    except ValueError:
                        response = json.dumps({
                            "type": "error",
                            "message": "Veuillez envoyer un entier valide ou 'getdata'."
                        })
                
                # Envoyer la réponse WebSocket
                writer.write(create_websocket_frame(response))
                await writer.drain()
                
            elif opcode == 0x8:  # Close frame
                print(f"Fermeture de connexion reçue de {client_info}")
                writer.write(b"\x88\x00")
                await writer.drain()
                break
            
    except Exception as e:
        print(f"Erreur avec le client {client_info}: {e}")
    finally:
        print(f"Connexion fermée avec {client_info}")
        if writer in clients:
            clients.remove(writer)
        await writer.aclose()

# Test simple des capteurs HC-SR04
def test_hcsr04():
    print("\n--- Test des capteurs HC-SR04 ---")
    try:
        print("Capteur 1:")
        dist1 = measure_distance(trigger1, echo1)
        print(f"Distance: {dist1} cm")
    except Exception as e:
        print(f"Erreur capteur 1: {e}")
    
    try:
        print("Capteur 2:")
        dist2 = measure_distance(trigger2, echo2)
        print(f"Distance: {dist2} cm")
    except Exception as e:
        print(f"Erreur capteur 2: {e}")
    print("-------------------------------\n")

async def main():
    # Importer Math ici pour éviter les problèmes d'initialisation
    global math
    import math
    
    # Tester les capteurs à ultrasons
    test_hcsr04()
    
    try:
        ip = connect_to_wifi()
        port = 8765
        print(f"Démarrage du serveur WebSocket sur ws://{ip}:{port}")
    except Exception as e:
        print(f"Erreur de connexion Wi-Fi: {e}")
        ip = "0.0.0.0"
        port = 8765
    
    # Liste des clients connectés
    clients = []
    
    try:
        # Afficher un message de démarrage sur l'écran LCD
        if lcd:
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.putstr("Serveur WebSocket")
            lcd.move_to(0, 1)
            lcd.putstr(f"IP:{ip}")
            time.sleep(2)
        
        # Démarrer les tâches asynchrones
        asyncio.create_task(sensor_task(clients))
        asyncio.create_task(gps_task())
        asyncio.create_task(lcd_update_task())
        asyncio.create_task(websocket_update_task(clients))
        
        # Fonction de gestion des connexions
        async def handle_client(reader, writer):
            await websocket_handler(reader, writer, clients)
        
        server = await asyncio.start_server(handle_client, "0.0.0.0", port)
        print(f"Serveur WebSocket démarré et prêt à accepter des connexions")
        
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Erreur serveur: {e}")

try:
    # Tests initiaux et exécution du programme principal
    print("Démarrage du programme - Version: 2025-05-16")
    asyncio.run(main())
except KeyboardInterrupt:
    print("Arrêt du serveur...")
finally:
    # Nettoyage
    servo.duty_u16(0)
    if lcd:
        lcd.clear()
        lcd.backlight_off()