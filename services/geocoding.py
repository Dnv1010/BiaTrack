"""
Servicio de geocoding para convertir ciudades a coordenadas
Usa Nominatim (OpenStreetMap) como servicio gratuito
"""

import requests
from typing import Optional, Dict, Tuple
import time

def geocode_city(city_name: str, country: str = "Colombia") -> Optional[Dict]:
    """
    Obtiene coordenadas de una ciudad usando Nominatim
    
    Args:
        city_name: Nombre de la ciudad
        country: País (default: Colombia)
    
    Returns:
        dict con 'lat' y 'lon', o None si no se encuentra
    """
    try:
        query = f"{city_name}, {country}"
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': query,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'co'
        }
        headers = {
            'User-Agent': 'BiaTrack/1.0'  # Requerido por Nominatim
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            result = data[0]
            return {
                'lat': float(result['lat']),
                'lon': float(result['lon']),
                'display_name': result.get('display_name', query)
            }
        
        return None
    except Exception as e:
        print(f"Error en geocoding para {city_name}: {e}")
        return None
    finally:
        # Rate limiting: Nominatim requiere 1 segundo entre requests
        time.sleep(1)

def buscar_ciudad(query: str) -> list:
    """
    Busca ciudades que coincidan con el query (autocompletar)
    
    Args:
        query: Texto de búsqueda
    
    Returns:
        Lista de ciudades encontradas con coordenadas
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': f"{query}, Colombia",
            'format': 'json',
            'limit': 5,
            'countrycodes': 'co',
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'BiaTrack/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data:
            # Filtrar solo ciudades/poblaciones
            if item.get('type') in ['city', 'town', 'village', 'administrative']:
                results.append({
                    'name': item.get('display_name', '').split(',')[0],
                    'full_name': item.get('display_name', ''),
                    'lat': float(item['lat']),
                    'lon': float(item['lon'])
                })
        
        return results
    except Exception as e:
        print(f"Error en búsqueda de ciudad: {e}")
        return []
    finally:
        time.sleep(1)

