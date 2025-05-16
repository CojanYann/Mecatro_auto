from shapely.geometry import Point, Polygon

# Définition des points GPS qui forment le polygone (dans l'ordre)
points = [
    (47.571300, -3.072753),
    (47.571389, -3.072347),
    (47.571595, -3.071556),
    (47.571357, -3.071503),
    (47.571164, -3.072600)
]

# Créer un polygone avec les points GPS
polygon = Polygon(points)

# Fonction pour vérifier si un point est à l'intérieur ou à l'extérieur du polygone
def is_point_in_polygon(lat, lon):
    point = Point(lat, lon)
    if polygon.contains(point):
        return "Le point est à l'intérieur du polygone."
    else:
        return "Le point est à l'extérieur du polygone."

point_to_check = (47.571449, -3.071929)
result = is_point_in_polygon(*point_to_check)
print(result)