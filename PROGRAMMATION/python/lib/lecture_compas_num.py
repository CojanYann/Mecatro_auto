from bmm150 import *
from time import *

print("Démarrage du programme...")
sleep(1)  # Laissez le capteur s'initialiser

def initialiser_compas():

    # Test avec différentes adresses possibles
    addresses = [0x13, 0x10, 0x11, 0x12]  # Essayer d'abord l'adresse 19 (0x13)
    address_names = {
        0x10: "ADDRESS_0 (CSB:0 SDO:0)",
        0x11: "ADDRESS_1 (CSB:0 SDO:1)",
        0x12: "ADDRESS_2 (CSB:1 SDO:0)",
        0x13: "ADDRESS_3 (CSB:1 SDO:1) par défaut"
    }
    
    for addr in addresses:
        try:
            print(f"Tentative avec l'adresse {addr} ({address_names.get(addr, 'inconnue')})")
            compas = bmm150_I2C(sdaPin=8, sclPin=9, addr=addr)
            print(f"Initialisation réussie avec l'adresse {addr}!")
            return compas
        except Exception as e:
            print(f"Échec avec l'adresse {addr}: {e}")
    
    print("Impossible d'initialiser le compas avec aucune adresse.")
    return None

def lecture_cap(compas):
    try:
        if compas is None:
            return None
            
        degree = compas.get_compass_degree()
        lectureCap = degree - 90
        if lectureCap < 0:
            lectureCap = lectureCap + 360
        return lectureCap
    except Exception as e:
        print(f"Erreur lors de la lecture du cap: {e}")
        return None

# Programme principal
try:
    # Initialisation du compas
    compasNumerique = initialiser_compas()
    
    if compasNumerique is not None:
        # Lecture du cap en boucle
        for i in range(20):
            cap = lecture_cap(compasNumerique)
            if cap is not None:
                print("Cap:", cap, "degrés")
            else:
                print("Erreur de lecture du cap")
            sleep(2)
    else:
        print("Impossible de continuer sans compas initialisé.")
except Exception as e:
    print(f"Erreur générale: {e}")

