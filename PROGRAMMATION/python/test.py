from machine import ADC, Timer
import _thread
import time

# Configuration du détecteur de métaux
SEUIL_DETECTION = 45000  # Seuil de détection (valeur ADC)
PIN_DETECTEUR = 26       # Numéro de la pin ADC
FREQ_ECHANTILLONNAGE = 100  # Hz

# Variables globales
metal_detecte = False
adc_detecteur = ADC(PIN_DETECTEUR)  # Initialise l'ADC sur la pin 26

def surveillance_detecteur():
    """
    Fonction exécutée dans un thread séparé pour surveiller 
    en permanence le détecteur de métaux
    """
    global metal_detecte
    
    # Créer un timer pour échantillonner régulièrement
    timer = Timer()
    
    def check_metal(t):
        global metal_detecte
        valeur = adc_detecteur.read_u16()
        if valeur > SEUIL_DETECTION:
            metal_detecte = True
            print(f"!!! MÉTAL DÉTECTÉ !!! Valeur: {valeur}")
    
    # Initialisation du timer pour vérifier à intervalles réguliers
    timer.init(freq=FREQ_ECHANTILLONNAGE, mode=Timer.PERIODIC, callback=check_metal)
    
    # Boucle infinie pour maintenir le thread actif
    while True:
        time.sleep(0.1)  # Évite de surcharger le CPU

def demarrer_surveillance():
    """
    Démarre la surveillance du détecteur de métaux dans un thread séparé
    """
    _thread.start_new_thread(surveillance_detecteur, ())
    print("Surveillance du détecteur de métaux démarrée")

def lecture_det_metaux():
    """
    Vérifie si du métal a été détecté
    
    Returns:
        bool: True si du métal est détecté, False sinon
    """
    global metal_detecte
    
    # Si du métal est détecté, réinitialiser le drapeau et renvoyer True
    if metal_detecte:
        resultat = True
        metal_detecte = False  # Réinitialiser pour la prochaine détection
        return resultat
    
    return False

# Démarrer automatiquement la surveillance lors de l'importation de ce module
demarrer_surveillance()