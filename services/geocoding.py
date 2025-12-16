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
        # Validar entrada
        if not city_name or not city_name.strip():
            print(f"[ERROR] Nombre de ciudad vacío")
            return None
        
        city_name = city_name.strip()
        
        # Si ya contiene "Colombia" o parece una dirección completa, usar directamente
        if ', Colombia' in city_name or city_name.count(',') >= 2:
            query = city_name
        else:
            query = f"{city_name}, {country}"
        
        print(f"[DEBUG] Geocoding query: {query}")
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': query,
            'format': 'json',
            'limit': 5,  # Aumentar límite para tener más opciones
            'countrycodes': 'co',
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'BiaTrack/1.0'  # Requerido por Nominatim
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        print(f"[DEBUG] Nominatim retornó {len(data) if data else 0} resultados")
        
        if data and len(data) > 0:
            # Priorizar resultados de tipo city, town, village, administrative
            preferred_types = ['city', 'town', 'village', 'administrative']
            
            # Buscar primero resultados preferidos
            for result in data:
                if result.get('type') in preferred_types or result.get('class') == 'place':
                    return {
                        'lat': float(result['lat']),
                        'lon': float(result['lon']),
                        'display_name': result.get('display_name', query),
                        'type': result.get('type', 'unknown'),
                        'class': result.get('class', 'unknown')
                    }
            
            # Si no hay preferidos, usar el primero
            result = data[0]
            return {
                'lat': float(result['lat']),
                'lon': float(result['lon']),
                'display_name': result.get('display_name', query),
                'type': result.get('type', 'unknown'),
                'class': result.get('class', 'unknown')
            }
        
        print(f"[WARNING] No se encontraron resultados para: {query}")
        return None
    except requests.exceptions.Timeout:
        print(f"[ERROR] Timeout al geocodificar {city_name}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error de red al geocodificar {city_name}: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Error en geocoding para {city_name}: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Rate limiting: Nominatim requiere 1 segundo entre requests
        time.sleep(1)

def buscar_ciudad(query: str) -> list:
    """
    Busca ciudades y direcciones que coincidan con el query (autocompletar)
    Ahora acepta tanto ciudades como direcciones completas con comas
    
    Args:
        query: Texto de búsqueda (puede ser ciudad o dirección completa con comas)
              Ejemplos: "Barrancabermeja", "Calle 123, Barrancabermeja", "Carrera 45 # 12-34, Medellín"
    
    Returns:
        Lista de resultados encontrados con coordenadas
    """
    try:
        # Si el query ya contiene comas, probablemente es una dirección completa
        # Si contiene "Colombia", usar directamente; si no, agregar ", Colombia"
        if ', Colombia' in query:
            search_query = query
        elif query.count(',') >= 1:
            # Ya tiene comas (ej: "Calle 123, Barrancabermeja"), agregar ", Colombia" al final
            search_query = f"{query}, Colombia"
        else:
            # Solo ciudad, agregar ", Colombia"
            search_query = f"{query}, Colombia"
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': search_query,
            'format': 'json',
            'limit': 15,  # Aumentado para incluir más resultados de direcciones
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
            
            # Incluir ciudades, pueblos, direcciones, lugares, calles, edificios, etc.
            if item_type in ['city', 'town', 'village', 'administrative', 'road', 'house', 'building', 'place', 'residential', 'commercial']:
                # Usar el nombre completo para evitar duplicados
                if display_name not in seen_names:
                    seen_names.add(display_name)
                    # Para el nombre corto, usar la primera parte antes de la primera coma
                    # pero si es una dirección con comas, mantener más contexto
                    parts = display_name.split(',')
                    if len(parts) > 2:
                        # Dirección completa: usar las primeras 2 partes (ej: "Calle 123, Barrancabermeja")
                        short_name = ', '.join(parts[:2]).strip()
                    else:
                        # Solo ciudad: usar la primera parte
                        short_name = parts[0].strip()
                    
                    results.append({
                        'name': short_name,
                        'full_name': display_name,  # Nombre completo con todas las comas
                        'lat': float(item['lat']),
                        'lon': float(item['lon']),
                        'type': item_type,
                        'class': item_class
                    })
        
        return results[:15]  # Limitar a 15 resultados
    except Exception as e:
        print(f"Error en búsqueda de ciudad/dirección: {e}")
        return []
    finally:
        time.sleep(1)

