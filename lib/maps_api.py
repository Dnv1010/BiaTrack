"""
Integración con Google Maps Distance Matrix API
Obtiene distancia y tiempo automáticamente
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_KM_PER_GALLON = 30  # Valor por defecto para vehículos livianos (Categoría I)

def get_route_data(origin: str, destination: str) -> dict:
    """
    Obtiene distancia y tiempo desde Google Maps Distance Matrix API
    
    Args:
        origin: Ciudad de origen
        destination: Ciudad de destino
    
    Returns:
        dict: {
            'distanceKm': float,
            'durationMinutes': int,
            'error': str (opcional)
        }
    """
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not api_key:
        return {
            'distanceKm': 0,
            'durationMinutes': 0,
            'error': 'API Key de Google Maps no configurada. Configura GOOGLE_MAPS_API_KEY en .env'
        }
    
    try:
        # Preparar URLs
        origin_encoded = f"{origin}, Colombia"
        destination_encoded = f"{destination}, Colombia"
        
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            'origins': origin_encoded,
            'destinations': destination_encoded,
            'units': 'metric',
            'language': 'es',
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'OK' and data.get('rows', [{}])[0].get('elements', [{}])[0].get('status') == 'OK':
            element = data['rows'][0]['elements'][0]
            distance_km = element['distance']['value'] / 1000  # Convertir de metros a km
            duration_minutes = round(element['duration']['value'] / 60)  # Convertir de segundos a minutos
            
            return {
                'distanceKm': round(distance_km, 2),
                'durationMinutes': duration_minutes,
                'error': None
            }
        else:
            error_msg = data.get('error_message', 'No se pudo obtener la ruta')
            return {
                'distanceKm': 0,
                'durationMinutes': 0,
                'error': error_msg
            }
    
    except requests.exceptions.RequestException as e:
        return {
            'distanceKm': 0,
            'durationMinutes': 0,
            'error': f'Error al consultar la API: {str(e)}'
        }
    except Exception as e:
        return {
            'distanceKm': 0,
            'durationMinutes': 0,
            'error': f'Error inesperado: {str(e)}'
        }

