"""
Servicio de geocoding para convertir ciudades a coordenadas
Usa Nominatim (OpenStreetMap) como servicio gratuito
"""

import requests
from typing import Optional, Dict, Tuple
import time

def geocode_city(city_name: str, country: str = "Colombia") -> Optional[Dict]:
    """
    Obtiene coordenadas de una ciudad o dirección usando Nominatim
    Ahora acepta tanto ciudades como direcciones completas
    
    Args:
        city_name: Nombre de la ciudad o dirección completa
        country: País (default: Colombia)
    
    Returns:
        dict con 'lat', 'lon' y 'display_name', o None si no se encuentra
    """
    try:
        # Si ya contiene "Colombia" o parece una dirección completa, usar directamente
        if ', Colombia' in city_name or city_name.count(',') >= 2:
            query = city_name
        else:
            query = f"{city_name}, {country}"
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': query,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'co',
            'addressdetails': 1
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
                'display_name': result.get('display_name', query),
                'type': result.get('type', 'unknown'),
                'class': result.get('class', 'unknown')
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
    Busca ciudades y direcciones que coincidan con el query (autocompletar)
    Ahora acepta tanto ciudades como direcciones completas
    
    Args:
        query: Texto de búsqueda (puede ser ciudad o dirección)
    
    Returns:
        Lista de resultados encontrados con coordenadas
    """
    try:
        # Si parece una dirección completa (contiene números o muchas comas), buscar directamente
        search_query = f"{query}, Colombia" if ', Colombia' not in query else query
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': search_query,
            'format': 'json',
            'limit': 10,  # Aumentado para incluir más resultados
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
        seen_names = set()  # Para evitar duplicados
        
        for item in data:
            display_name = item.get('display_name', '')
            item_type = item.get('type', '')
            item_class = item.get('class', '')
            
            # Incluir ciudades, pueblos, direcciones, lugares, etc.
            if item_type in ['city', 'town', 'village', 'administrative', 'road', 'house', 'building', 'place']:
                # Usar el nombre completo para evitar duplicados
                if display_name not in seen_names:
                    seen_names.add(display_name)
                    # Extraer nombre corto (primera parte antes de la primera coma)
                    short_name = display_name.split(',')[0].strip()
                    
                    results.append({
                        'name': short_name,
                        'full_name': display_name,
                        'lat': float(item['lat']),
                        'lon': float(item['lon']),
                        'type': item_type,
                        'class': item_class
                    })
        
        return results[:10]  # Limitar a 10 resultados
    except Exception as e:
        print(f"Error en búsqueda de ciudad/dirección: {e}")
        return []
    finally:
        time.sleep(1)

