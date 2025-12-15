"""
Servicio de routing usando OSRM (Open Source Routing Machine)
Calcula rutas con distancia, tiempo y geometría
"""

import requests
from typing import Optional, Dict, List, Tuple
import json

def calcular_ruta_con_trafico(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float
) -> Optional[Dict]:
    """
    Calcula ruta usando OSRM con información de tráfico
    
    Args:
        origin_lat, origin_lon: Coordenadas de origen
        dest_lat, dest_lon: Coordenadas de destino
    
    Returns:
        dict con distancia (km), duración (min), geometría, etc.
    """
    try:
        # OSRM public demo server (puede tener límites de uso)
        # En producción, usaría un servidor OSRM propio o servicio pago
        base_url = "https://router.project-osrm.org"
        
        # Endpoint de route con geometría
        url = f"{base_url}/route/v1/driving/{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
        params = {
            'overview': 'full',  # Geometría completa de la ruta
            'geometries': 'geojson',
            'steps': 'true',
            'alternatives': 'false'
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get('code') != 'Ok':
            return None
        
        route = data['routes'][0]
        distance_m = route['distance']  # en metros
        duration_s = route['duration']  # en segundos
        
        # Calcular tiempo con factor de hora pico (3.5x según especificación)
        duration_normal_min = int(duration_s / 60)
        duration_peak_min = int(duration_normal_min * 3.5)
        
        return {
            'distance_km': round(distance_m / 1000, 2),
            'duration_normal_min': duration_normal_min,
            'duration_peak_min': duration_peak_min,
            'geometry': route.get('geometry'),  # GeoJSON LineString
            'legs': route.get('legs', []),
            'steps': route.get('legs', [{}])[0].get('steps', []) if route.get('legs') else []
        }
    except Exception as e:
        print(f"Error calculando ruta: {e}")
        return None

def calcular_ruta_inversa(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float
) -> Optional[Dict]:
    """
    Calcula ruta de regreso (destino -> origen)
    """
    return calcular_ruta_con_trafico(dest_lat, dest_lon, origin_lat, origin_lon)

