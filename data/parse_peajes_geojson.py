"""
Script para parsear el archivo GeoJSON de peajes oficiales de INVIAS
y convertirlo al formato usado por BiaTrack
"""

import json
import os
from typing import List, Dict, Any

# Mapeo de códigos territoriales a nombres de departamentos
TERRITORIAL_MAPPING = {
    "1": "Antioquia",
    "2": "Atlántico",
    "3": "Bolívar",
    "4": "Boyacá",
    "5": "Caldas",
    "6": "Caquetá",
    "7": "Cauca",
    "8": "Cesar",
    "9": "Córdoba",
    "10": "Cundinamarca",
    "11": "Huila",
    "12": "La Guajira",
    "13": "Magdalena",
    "14": "Meta",
    "15": "Nariño",
    "16": "Norte de Santander",
    "17": "Quindío",
    "18": "Risaralda",
    "19": "Santander",
    "20": "Sucre",
    "21": "Tolima",
    "22": "Valle del Cauca",
    "23": "Arauca",
    "24": "Casanare",
    "25": "Putumayo",
    "26": "San Andrés",
    "27": "Amazonas",
    "28": "Guainía",
    "29": "Guaviare",
    "30": "Vaupés",
    "31": "Vichada",
    "32": "Bogotá D.C."
}

def get_department_from_territorial(territorial: Any) -> str:
    """Obtiene el nombre del departamento desde el código territorial"""
    if territorial is None:
        return None
    
    territorial_str = str(territorial).strip()
    return TERRITORIAL_MAPPING.get(territorial_str, None)


def get_fare_from_categories(props: Dict) -> int:
    """
    Obtiene la tarifa del peaje desde las categorías
    Usa categoriai (Categoría I) como tarifa base para vehículos ligeros
    """
    # Intentar obtener categoriai primero
    fare = props.get('categoriai') or props.get('categoriaI') or 0
    
    # Si no hay categoriai, intentar categoriaii
    if fare == 0:
        fare = props.get('categoriaii') or props.get('categoriaII') or 0
    
    # Convertir a entero
    try:
        return int(float(fare))
    except (ValueError, TypeError):
        return 0


def is_toll_active(props: Dict) -> bool:
    """Determina si un peaje está activo basándose en sus propiedades"""
    nombre = props.get('nombrepeaje', '').upper()
    
    # Si el nombre contiene "NO OPERATIVO" o similar, no está activo
    if 'NO OPERATIVO' in nombre or 'DESMONTADO' in nombre or 'SUSPENDIDO' in nombre:
        return False
    
    # Si no tiene tarifa, probablemente no está activo
    fare = get_fare_from_categories(props)
    if fare == 0:
        return False
    
    return True


def parse_peajes_geojson(geojson_path: str) -> List[Dict]:
    """
    Parsea el archivo GeoJSON de peajes y lo convierte al formato de BiaTrack
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
        
        # Obtener coordenadas desde geometry (más confiable)
        coordinates = None
        if geometry.get('type') == 'Point':
            coords = geometry.get('coordinates', [])
            if len(coords) >= 2:
                lon, lat = coords[0], coords[1]
                if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                    coordinates = {'latitude': float(lat), 'longitude': float(lon)}
        
        # Si no hay coordenadas en geometry, intentar desde propiedades
        if not coordinates:
            lat = props.get('latitud')
            lon = props.get('longitud')
            # Verificar que no sean el mismo valor (error común en los datos)
            if lat and lon and lat != lon and isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                try:
                    coordinates = {'latitude': float(lat), 'longitude': float(lon)}
                except (ValueError, TypeError):
                    coordinates = None
        
        # Si aún no hay coordenadas válidas, saltar este peaje
        if not coordinates:
            continue
        
        # Nombre del peaje
        name = props.get('nombrepeaje', '').strip()
        if not name:
            continue
        
        # Departamento
        territorial = props.get('territorial') or props.get('territoria')
        department = get_department_from_territorial(territorial)
        
        # Operador/Responsable
        operator = props.get('responsable', '').strip() or props.get('administrador', '').strip() or None
        
        # Tarifa
        fare = get_fare_from_categories(props)
        
        # Estado
        status = 'ACTIVE' if is_toll_active(props) else 'SUSPENDED'
        
        # Crear objeto de peaje
        toll = {
            'id': f'invias_geojson_{props.get("objectid", idx + 1)}',
            'name': name,
            'department': department or 'Colombia',
            'operator': operator,
            'status': status,
            'fare_cop': fare,
            'latitude': coordinates['latitude'],
            'longitude': coordinates['longitude'],
        }
        
        # Agregar información adicional si está disponible
        if props.get('codigotramo'):
            toll['codigo_via'] = props.get('codigotramo')
        if props.get('sector'):
            toll['sector'] = props.get('sector')
        if props.get('ubicacion'):
            toll['ubicacion'] = props.get('ubicacion')
        
        tolls.append(toll)
    
    return tolls


def merge_with_existing_tolls(geojson_tolls: List[Dict], existing_tolls_path: str = 'data/tolls_data.json') -> List[Dict]:
    """
    Fusiona los peajes del GeoJSON con los peajes existentes
    Prioriza los existentes si tienen el mismo nombre
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
    geojson_names_used = set()
    
    # Primero agregar todos los peajes existentes (tienen tarifas actualizadas)
    for toll in existing_tolls:
        merged_tolls.append(toll)
        name_normalized = toll.get('name', '').upper().strip()
        geojson_names_used.add(name_normalized)
    
    # Luego agregar peajes del GeoJSON que no están en los existentes
    for toll in geojson_tolls:
        name_normalized = toll.get('name', '').upper().strip()
        
        # Si ya existe uno con el mismo nombre, intentar fusionar datos
        if name_normalized in existing_by_name:
            existing = existing_by_name[name_normalized]
            # Si el existente no tiene coordenadas pero el del GeoJSON sí, agregarlas
            if 'latitude' not in existing and 'latitude' in toll:
                existing['latitude'] = toll['latitude']
                existing['longitude'] = toll['longitude']
            # Si el existente no tiene operador pero el del GeoJSON sí, agregarlo
            if not existing.get('operator') and toll.get('operator'):
                existing['operator'] = toll['operator']
        else:
            # Es un peaje nuevo del GeoJSON, agregarlo
            merged_tolls.append(toll)
    
    return merged_tolls


def main():
    geojson_path = os.path.join(os.path.dirname(__file__), 'Peajes.geojson')
    output_path = os.path.join(os.path.dirname(__file__), 'tolls_data_geojson.json')
    merged_output_path = os.path.join(os.path.dirname(__file__), 'tolls_data.json')
    
    print("[INFO] Parseando GeoJSON de peajes...")
    geojson_tolls = parse_peajes_geojson(geojson_path)
    
    if not geojson_tolls:
        print("[ERROR] No se encontraron peajes en el archivo GeoJSON")
        return
    
    print(f"[OK] Se encontraron {len(geojson_tolls)} peajes en el GeoJSON")
    
    # Estadísticas del GeoJSON
    with_coords = sum(1 for t in geojson_tolls if 'latitude' in t)
    with_fare = sum(1 for t in geojson_tolls if t.get('fare_cop', 0) > 0)
    active = sum(1 for t in geojson_tolls if t.get('status') == 'ACTIVE')
    
    print(f"[STATS] GeoJSON:")
    print(f"   - Con coordenadas: {with_coords}")
    print(f"   - Con tarifa: {with_fare}")
    print(f"   - Activos: {active}")
    
    # Guardar solo los del GeoJSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson_tolls, f, ensure_ascii=False, indent=2)
    print(f"[OK] Guardado: {output_path}")
    
    # Fusionar con peajes existentes
    print("\n[INFO] Fusionando con peajes existentes...")
    merged_tolls = merge_with_existing_tolls(geojson_tolls)
    
    with open(merged_output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_tolls, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Guardado archivo fusionado: {merged_output_path}")
    print(f"[OK] Total de peajes: {len(merged_tolls)}")
    
    # Estadísticas finales
    final_with_coords = sum(1 for t in merged_tolls if 'latitude' in t)
    final_with_fare = sum(1 for t in merged_tolls if t.get('fare_cop', 0) > 0)
    final_active = sum(1 for t in merged_tolls if t.get('status') == 'ACTIVE')
    
    print(f"\n[STATS] Archivo fusionado:")
    print(f"   - Con coordenadas: {final_with_coords}")
    print(f"   - Con tarifa: {final_with_fare}")
    print(f"   - Activos: {final_active}")


if __name__ == "__main__":
    main()

