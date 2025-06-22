from bmm150 import *
from time import sleep
import machine

class CompasNumerique:
    def __init__(self, sda_pin=2, scl_pin=3, addr=19, i2c_id=1):
        try:
            # Vérifie que le compas est bien détecté
            i2c = machine.I2C(i2c_id, sda=machine.Pin(sda_pin), scl=machine.Pin(scl_pin), freq=400000)
            found = i2c.scan()
            if addr not in found:
                raise Exception(f"Compas non détecté à l'adresse {hex(addr)}. Adresses trouvées: {found}")
            # Utilise le constructeur de la lib bmm150
            self.compas = bmm150_I2C(sdaPin=sda_pin, sclPin=scl_pin, addr=addr)
            print(f"Compas initialisé à l'adresse {hex(addr)}")
        except Exception as e:
            print("Erreur d'initialisation du compas:", e)
            self.compas = None

    def is_connected(self):
        return self.compas is not None

    def lire_cap(self):
        if self.compas is None:
            return None
        try:
            degree = self.compas.get_compass_degree()
            lectureCap = degree - 90
            if lectureCap < 0:
                lectureCap += 360
            return lectureCap
        except Exception as e:
            print("Erreur lors de la lecture du cap:", e)
            return None

# Exemple d'utilisation
if __name__ == "__main__":
    print("Démarrage du programme...")
    sleep(1)
    compas = CompasNumerique(sda_pin=2, scl_pin=3, addr=19, i2c_id=1)
    if compas.is_connected():
        for i in range(20):
            cap = compas.lire_cap()
            if cap is not None:
                print("Cap:", cap, "degrés")
            else:
                print("Erreur de lecture du cap")
            sleep(2)
    else:
        print("Impossible de continuer sans compas initialisé.")

