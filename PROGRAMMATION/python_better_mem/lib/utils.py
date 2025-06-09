from math import sqrt, atan2, degrees
import machine
import urequests
import gc

def i2cscan(sda=8, scl=9):
    i2c = machine.I2C(0, sda=sda, scl=scl, freq=400000)
    result = i2c.scan()
    del i2c  # Libère l'objet I2C
    gc.collect()
    return result

# Polygone statique pour économiser mémoire
polygon_points = [
    (48.602725, -3.834250),
    (48.291210, -3.583421),
    (48.507350, -2.793577),
    (47.701964, -2.702852),
    (47.999214, -4.149120)
]

def distance(point1, point2):
    """Calcul optimisé de distance"""
    x1, y1 = point1
    x2, y2 = point2
    dx = x2 - x1
    dy = y2 - y1
    return sqrt(dx * dx + dy * dy)

def closest_point_on_segment(px, py, ax, ay, bx, by):
    """Version optimisée sans variables temporaires inutiles"""
    apx = px - ax
    apy = py - ay
    abx = bx - ax
    aby = by - ay
    
    ab_squared = abx * abx + aby * aby
    if ab_squared == 0:
        return (ax, ay)
    
    t = max(0, min(1, (apx * abx + apy * aby) / ab_squared))
    return (ax + t * abx, ay + t * aby)

def find_closest_point_polygon(lat, lon, polygon):
    """Version optimisée avec moins d'allocations"""
    if not polygon:
        return None
    
    closest_point = None
    min_distance = float('inf')
    num_points = len(polygon)
    
    for i in range(num_points):
        ax, ay = polygon[i]
        bx, by = polygon[(i + 1) % num_points]
        
        candidate_point = closest_point_on_segment(lat, lon, ax, ay, bx, by)
        candidate_distance = distance((lat, lon), candidate_point)
        
        if candidate_distance < min_distance:
            min_distance = candidate_distance
            closest_point = candidate_point
    
    return closest_point

def calculate_cap(lat1, lon1, lat2, lon2):
    """Version optimisée du calcul de cap"""
    delta_lon = lon2 - lon1
    delta_lat = lat2 - lat1
    angle = atan2(delta_lon, delta_lat)
    bearing = (degrees(angle) + 360) % 360
    return bearing

def is_point_in_polygon(lat, lon, polygon):
    """Version optimisée ray-casting"""
    if not polygon:
        return False
    
    num_points = len(polygon)
    inside = False
    x, y = lat, lon
    
    j = num_points - 1
    for i in range(num_points):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    
    return inside

# Variable globale pour éviter les réallocations
_mode_check_counter = 0

def check_mode_auto(ip="192.168.6.235", port="5000"):
    """Version optimisée avec cache et nettoyage mémoire"""
    global _mode_check_counter
    
    # Éviter trop de requêtes réseau
    _mode_check_counter += 1
    if _mode_check_counter % 10 != 0:  # Check seulement 1 fois sur 10
        return True
    
    try:
        url = f"http://{ip}:{port}/api/mode"
        response = urequests.get(url)
        
        if response.status_code == 200:
            content = response.text
            is_manual = '"manuel"' in content
            response.close()
            del response, content
            gc.collect()
            return not is_manual
        else:
            response.close()
            del response  
            gc.collect()
            return True
            
    except Exception as e:
        print("Erreur vérification mode:", e)
        gc.collect()
        return True

if __name__ == "__main__":
    # Test optimisé
    test_point = (47, 2)
    result = is_point_in_polygon(test_point[0], test_point[1], polygon_points)
    print(f"Point {test_point} dans polygone: {result}")
    gc.collect()