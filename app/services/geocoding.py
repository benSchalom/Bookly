import requests
from math import radians, sin, cos, sqrt, atan2

def geocoder_adresse(adresse):
    # utilisation du service Nominatim pour avoir 
    # la latitude et la longitude d'une adresse

    url = 'https://nominatim.openstreetmap.org/search'

    params = {
        'q': adresse,
        'format': 'json',
        'limit': 1
    }

    headers = {
        'User-Agent': 'AsteurApp/1.0'  
    }
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    if data and len(data) > 0:
        return float(data[0]['lat']), float(data[0]['lon'])
    
    return None, None


def calculer_distance(lat1, lon1, lat2, lon2):
    """Calcule distance en km entre 2 points (formule Haversine)"""
    R = 6371  # Rayon Terre en km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return round(R * c, 2)