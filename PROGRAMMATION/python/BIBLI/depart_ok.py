def depart_ok():
    all_capteur = all_capteur()
    if all_capteur:
        print("Robot prêt à partir")
        return True
    else:
        print("Robot pas prêt à partir")
        return False

def all_capteur():
    capteur_obstacle = True
    capteur_gps = True
    capteur_compas = True
    capteur_benne = True
    if capteur_obstacle and capteur_gps and capteur_compas and capteur_benne:
        return True
    else:
        return False