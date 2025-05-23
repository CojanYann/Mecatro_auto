from lecture_gps_fct import GPS
from lecture_ultrason import CapteurUltrason
from lecture_compas_num import CompasNumerique
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
    capteur = CapteurUltrason(trig=7, echo=6)

    if capteur.is_connected():
        sleep(0.5)
        print("Capteur initialisé avec succès")
        dist = capteur.mesure_distance()
        if dist is not None:
            print("Distance: {:.2f} cm".format(dist))
        else:
            print("Distance non détectée.")
        return capteur
    else:
        print("Capteur obstacle non connecté.")
        return False

def init_capteur_compas():
    try:
        Compas = CompasNumerique(sda_pin=2, scl_pin=3, addr=0x13, i2c_id=1)
        if Compas.is_connected():
            sleep(0.3)
            print("Compas initialisé avec succès")
            lectureCap = Compas.lire_cap()
            if lectureCap is not None:
                print("Lecture du cap:", lectureCap)
            else:
                print("Erreur de lecture du cap")
            return Compas
        else:
            print("Erreur de connexion au compas")
            return False
    except Exception as e:
        print(f"Erreur lors de l'initialisation du Compas: {e}")
        return False

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