from math import sqrt, atan2, degrees
import machine


def i2cscan(sda=8, scl=9):
    i2c = machine.I2C(0,sda=sda,scl=scl, freq=400000)
    return(i2c.scan())

# Définition des points GPS qui forment le polygone (dans l'ordre)
#morlaix-carhaix-stBrieux-Vannes-Quimper
# polygon_points = [
#     (48.602725, -3.834250),
#     (48.291210, -3.583421),
#     (48.507350, -2.793577),
#     (47.701964, -2.702852),
#     (47.999214, -4.149120)
# ]

# Calculer la distance entre deux points GPS
def distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Trouver le point du polygone le plus proche d'un point donné
# point du segement a, b poit donné p
def closest_point_on_segment(px, py, ax, ay, bx, by):
    # Projection du point (px, py) sur le segment (a, b)
    #vercteur AP -> ap
    apx, apy = px - ax, py - ay
    #Vecteur AB -> ab
    abx, aby = bx - ax, by - ay
    # cacrré des longueur pour pas avoir de racine car on travail juste en proportion
    ab_squared = abx ** 2 + aby ** 2
    if ab_squared == 0:
        return (ax, ay)  # Le segment est un point
    #calcul du parametre t 
    t = max(0, min(1, (apx * abx + apy * aby) / ab_squared))
    # partir du point A, on se déplace de t fois la longueur du vecteur AB vers le point projeté
    closest_x = ax + t * abx
    closest_y = ay + t * aby
    return (closest_x, closest_y)

# Trouver le point le plus proche sur le polygone
def find_closest_point_polygon(lat, lon, polygon):
    closest_point = None
    min_distance = float('inf')
    for i in range(len(polygon)):
        ax, ay = polygon[i]
        bx, by = polygon[(i + 1) % len(polygon)]  # Prochain sommet
        candidate_point = closest_point_on_segment(lat, lon, ax, ay, bx, by)
        candidate_distance = distance((lat, lon), candidate_point)
        if candidate_distance < min_distance:
            min_distance = candidate_distance
            closest_point = candidate_point
    return closest_point

# Calculer le cap en degrés entre deux points GPS
def calculate_cap(lat1, lon1, lat2, lon2):
    delta_lon = lon2 - lon1
    delta_lat = lat2 - lat1
    angle = atan2(delta_lon, delta_lat)  # Angle en radians
    bearing = (degrees(angle) + 360) % 360  # Conversion en degrés
    return bearing


# Fonction pour vérifier si un point est à l'intérieur du polygone (algorithme Ray-Casting)
def is_point_in_polygon(lat, lon, polygon):
    num_points = len(polygon)
    inside = False

    x, y = lat, lon
    p1x, p1y = polygon[0]

    for i in range(num_points + 1):
        p2x, p2y = polygon[i % num_points]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside