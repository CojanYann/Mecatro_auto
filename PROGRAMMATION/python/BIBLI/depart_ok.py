from lecture_gps_fct import GPS
from pico_i2c_lcd import I2cLcd
from time import sleep

def depart_ok():
    capteur_obstacle = init_capteur_obstacle()
    capteur_gps = init_gps()
    capteur_compas = init_capteur_compas()
    ecran_lcd = init_ecran_lcd()
    if all_capteurs([capteur_obstacle, capteur_gps, capteur_compas, ecran_lcd]):
        print("Robot prêt à partir")
        lon, lat = capteur_gps.read()
        print(lon, lat)
        return capteur_gps, ecran_lcd, capteur_compas, capteur_obstacle
    else:
        print("Robot pas prêt à partir")
        return False

def all_capteurs(status_list):
    # Vérifie que tous les capteurs sont True
    return all(status_list)

def init_capteur_obstacle():
    # Placeholder pour l'initialisation réelle
    return True

def init_capteur_compas():
    # Placeholder pour l'initialisation réelle
    return True

def init_ecran_lcd():
    try:
        lcd_device = I2cLcd()
        if lcd_device.is_connected():
            print("LCD initialisé avec succès")
            lcd_device.putstr("LCD OK")
            return lcd_device
        else:
            print("Erreur de connexion LCD")
            return False
    except Exception as e:
        print(f"Erreur lors de l'initialisation du LCD: {e}")
        return False

def init_gps(max_attempts=30, delay=1):
    gps_device = GPS()
    for i in range(max_attempts):
        gps_data = gps_device.read()
        if isinstance(gps_data, tuple) and len(gps_data) == 2:
            print("GPS initialisé avec succès")
            return gps_device
        else:
            print(f"Initialisation du GPS en cours... (tentative {i+1}/{max_attempts})")
            sleep(delay)
    print("Erreur d'initialisation du GPS")
    return False

# Pour test manuel
if __name__ == "__main__":
    depart_ok()