"""
Script para convertir los datos de peajes de INVIAS (GeoJSON) 
al formato usado por BiaTrack
"""

import json
import os
from typing import List, Dict, Any

# Mapeo de departamentos comunes
DEPARTMENT_MAPPING = {
    'ANTIOQUIA': 'Antioquia',
    'ATLANTICO': 'Atlántico',
    'BOGOTA': 'Cundinamarca',
    'BOLIVAR': 'Bolívar',
    'BOYACA': 'Boyacá',
    'CALDAS': 'Caldas',
    'CAQUETA': 'Caquetá',
    'CAUCA': 'Cauca',
    'CESAR': 'Cesar',
    'CORDOBA': 'Córdoba',
    'CUNDINAMARCA': 'Cundinamarca',
    'HUILA': 'Huila',
    'LA_GUAJIRA': 'La Guajira',
    'MAGDALENA': 'Magdalena',
    'META': 'Meta',
    'NARINO': 'Nariño',
    'NORTE_DE_SANTANDER': 'Norte de Santander',
    'QUINDIO': 'Quindío',
    'RISARALDA': 'Risaralda',
    'SANTANDER': 'Santander',
    'SUCRE': 'Sucre',
    'TOLIMA': 'Tolima',
    'VALLE_DEL_CAUCA': 'Valle del Cauca',
}

def normalize_department(territoria: str) -> str:
    """Normaliza el nombre del departamento"""
    if not territoria:
        return None
    
    territoria_upper = territoria.upper().strip()
    
    # Buscar coincidencias parciales
    for key, value in DEPARTMENT_MAPPING.items():
        if key in territoria_upper or territoria_upper in key:
            return value
    
    # Si no hay coincidencia, devolver el original capitalizado
    return territoria.title()


def parse_invias_geojson(geojson_path: str) -> List[Dict[str, Any]]:
    """
    Convierte el GeoJSON de INVIAS al formato de BiaTrack
    """
    if not os.path.exists(geojson_path):
        print(f"[ERROR] Archivo no encontrado: {geojson_path}")
        return []
    
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    tolls = []
    
    for idx, feature in enumerate(geojson_data.get('features', [])):
        props = feature.get('properties', {})
        geometry = feature.get('geometry', {})
        
        # Obtener coordenadas
        coordinates = None
        if geometry.get('type') == 'Point':
            coords = geometry.get('coordinates', [])
            if len(coords) >= 2:
                # GeoJSON usa [lon, lat], nosotros usamos [lat, lon]
                lon, lat = coords[0], coords[1]
                coordinates = {'latitude': lat, 'longitude': lon}
        
        # Si no hay coordenadas en geometry, intentar desde propiedades
        if not coordinates:
            lat = props.get('latsig') or props.get('lat')
            lon = props.get('longsig') or props.get('lon') or props.get('lng')
            if lat and lon:
                try:
                    coordinates = {'latitude': float(lat), 'longitude': float(lon)}
                except (ValueError, TypeError):
                    coordinates = None
        
        # Nombre del peaje
        name = props.get('nombre', '').strip()
        if not name:
            continue  # Saltar si no hay nombre
        
        # Departamento
        department = normalize_department(props.get('territoria', ''))
        
        # Operador/Administrador
        operator = props.get('administra', '').strip() or None
        
        # Código de vía
        codigo_via = props.get('codigo_via', '').strip() or None
        
        # Crear objeto de peaje
        toll = {
            'id': f'invias_{idx + 1}',
            'name': name,
            'department': department,
            'operator': operator,
            'status': 'ACTIVE',  # Asumimos que todos los de INVIAS están activos
            'fare_cop': 0,  # INVIAS no proporciona tarifas, se mantendrá 0 o se actualizará manualmente
        }
        
        # Agregar coordenadas si están disponibles
        if coordinates:
            toll['latitude'] = coordinates['latitude']
            toll['longitude'] = coordinates['longitude']
        
        # Agregar información adicional si está disponible
        if codigo_via:
            toll['codigo_via'] = codigo_via
        
        tolls.append(toll)
    
    return tolls


def merge_with_existing_tolls(invias_tolls: List[Dict], existing_tolls_path: str = 'data/tolls_data.json') -> List[Dict]:
    """
    Fusiona los peajes de INVIAS con los peajes existentes que tienen tarifas
    """
    existing_tolls = []
    
    if os.path.exists(existing_tolls_path):
        with open(existing_tolls_path, 'r', encoding='utf-8') as f:
            existing_tolls = json.load(f)
    
    # Crear un diccionario de peajes existentes por nombre normalizado
    existing_by_name = {}
    for toll in existing_tolls:
        name_normalized = toll.get('name', '').upper().strip()
        existing_by_name[name_normalized] = toll
    
    merged_tolls = []
    invias_names_used = set()
    
    # Primero agregar todos los peajes existentes (tienen tarifas)
    for toll in existing_tolls:
        merged_tolls.append(toll)
        name_normalized = toll.get('name', '').upper().strip()
        invias_names_used.add(name_normalized)
    
    # Luego agregar peajes de INVIAS que no están en los existentes
    for toll in invias_tolls:
        name_normalized = toll.get('name', '').upper().strip()
        
        # Si ya existe uno con el mismo nombre, intentar fusionar datos
        if name_normalized in existing_by_name:
            existing = existing_by_name[name_normalized]
            # Si el existente no tiene coordenadas pero el de INVIAS sí, agregarlas
            if 'latitude' not in existing and 'latitude' in toll:
                existing['latitude'] = toll['latitude']
                existing['longitude'] = toll['longitude']
            # Si el existente no tiene operador pero el de INVIAS sí, agregarlo
            if not existing.get('operator') and toll.get('operator'):
                existing['operator'] = toll['operator']
        else:
            # Es un peaje nuevo de INVIAS, agregarlo
            merged_tolls.append(toll)
    
    return merged_tolls


def main():
    geojson_path = os.path.join(os.path.dirname(__file__), 'peajes_colombia.geojson')
    output_path = os.path.join(os.path.dirname(__file__), 'tolls_data_invias.json')
    merged_output_path = os.path.join(os.path.dirname(__file__), 'tolls_data.json')
    
    print("[INFO] Parseando datos de INVIAS...")
    invias_tolls = parse_invias_geojson(geojson_path)
    
    if not invias_tolls:
        print("[ERROR] No se encontraron peajes en el archivo GeoJSON")
        return
    
    print(f"[OK] Se encontraron {len(invias_tolls)} peajes de INVIAS")
    
    # Guardar solo los de INVIAS
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(invias_tolls, f, ensure_ascii=False, indent=2)
    print(f"[OK] Guardado: {output_path}")
    
    # Fusionar con peajes existentes
    print("\n[INFO] Fusionando con peajes existentes...")
    merged_tolls = merge_with_existing_tolls(invias_tolls)
    
    with open(merged_output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_tolls, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Guardado archivo fusionado: {merged_output_path}")
    print(f"[OK] Total de peajes: {len(merged_tolls)}")
    
    # Estadísticas
    with_coords = sum(1 for t in merged_tolls if 'latitude' in t)
    with_fare = sum(1 for t in merged_tolls if t.get('fare_cop', 0) > 0)
    
    print(f"\n[STATS] Estadisticas:")
    print(f"   - Con coordenadas: {with_coords}")
    print(f"   - Con tarifa: {with_fare}")


if __name__ == "__main__":
    main()

