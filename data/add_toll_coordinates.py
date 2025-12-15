"""
Script para agregar coordenadas aproximadas a peajes conocidos
Basado en información de rutas principales
"""

import json
import os

# Coordenadas aproximadas de peajes principales en rutas conocidas
# Formato: nombre_peaje: (lat, lon)
TOLL_COORDINATES = {
    # Ruta Bucaramanga - Barrancabermeja (Ruta del Cacao)
    'La Lizama': (7.0647, -73.8547),  # Barrancabermeja
    'La Paz': (7.2000, -73.8000),  # Aproximado en la ruta
    'Lebrija': (7.1133, -73.2167),  # Lebrija, Santander
    
    # Otros peajes de Santander en rutas principales
    'Aguas Negras': (6.8333, -73.0833),  # Aproximado
    'Picacho': (7.3833, -73.2833),  # Aproximado
    'La Gómez': (7.2500, -73.1500),  # Aproximado
    'Los Curos': (7.0833, -73.1667),  # Aproximado
    'Oiba': (6.2667, -73.3000),  # Oiba
    'Río Blanco': (6.5000, -73.2500),  # Aproximado
    'Rionegro': (7.0167, -73.1500),  # Rionegro
    'Curití': (6.6167, -73.0667),  # Curití
    'Zambito': (6.7500, -73.0833),  # Aproximado
    
    # Peajes principales de otras rutas
    'Boquerón I': (4.6167, -74.0833),  # Bogotá - Medellín
    'Boquerón II': (4.6167, -74.0833),
    'La Línea': (4.6167, -75.3667),  # Túnel de La Línea
}

def add_coordinates_to_tolls():
    """Agrega coordenadas a peajes en el archivo JSON"""
    json_path = os.path.join('data', 'tolls_data.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        tolls = json.load(f)
    
    updated = 0
    for toll in tolls:
        name = toll.get('name', '').strip()
        
        # Buscar coordenadas por nombre exacto o parcial
        for toll_name, coords in TOLL_COORDINATES.items():
            if toll_name.lower() in name.lower() or name.lower() in toll_name.lower():
                if 'latitude' not in toll or not toll.get('latitude'):
                    toll['latitude'] = coords[0]
                    toll['longitude'] = coords[1]
                    updated += 1
                    print(f"Agregadas coordenadas a: {name} -> {coords}")
                break
    
    # Guardar archivo actualizado
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(tolls, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] Se actualizaron {updated} peajes con coordenadas")
    print(f"[OK] Total de peajes: {len(tolls)}")

if __name__ == '__main__':
    add_coordinates_to_tolls()

