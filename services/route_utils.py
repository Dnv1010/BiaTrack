"""
Utilidades para manipulación de rutas
Incluye funciones para truncar rutas desde un punto específico
"""

from typing import List, Tuple, Dict
from services.toll_calculator import (
    haversine_m,
    to_local_xy_m,
    point_segment_distance_m_xy,
    polyline_length_m,
    route_from_linestring
)

def find_point_on_route(route: List[Tuple[float, float]], target_point: Tuple[float, float]) -> Tuple[int, float]:
    """
    Encuentra el punto más cercano en la ruta a un punto objetivo
    Retorna el índice del segmento y la distancia acumulada hasta ese punto
    
    Args:
        route: Lista de puntos de la ruta [(lat, lon), ...]
        target_point: Punto objetivo (lat, lon)
    
    Returns:
        Tupla (segment_index, accumulated_distance_m)
        - segment_index: Índice del segmento donde está el punto más cercano
        - accumulated_distance_m: Distancia acumulada hasta ese punto
    """
    if len(route) < 2:
        return (0, 0.0)
    
    lat0, lon0 = route[0]
    px, py = to_local_xy_m(lat0, lon0, target_point[0], target_point[1])
    
    best_dist = float("inf")
    best_index = 0
    best_accumulated = 0.0
    accumulated = 0.0
    
    for i in range(len(route) - 1):
        seg_start = route[i]
        seg_end = route[i + 1]
        
        ax, ay = to_local_xy_m(lat0, lon0, seg_start[0], seg_start[1])
        bx, by = to_local_xy_m(lat0, lon0, seg_end[0], seg_end[1])
        
        # Distancia perpendicular del punto al segmento
        d_perp = point_segment_distance_m_xy(px, py, ax, ay, bx, by)
        
        # Calcular posición del punto proyectado en el segmento
        abx, aby = bx - ax, by - ay
        apx, apy = px - ax, py - ay
        ab2 = abx * abx + aby * aby
        
        if ab2 > 0:
            t = (apx * abx + apy * aby) / ab2
            t = max(0.0, min(1.0, t))
            
            # Distancia acumulada hasta el punto proyectado
            seg_length = haversine_m(seg_start, seg_end)
            dist_to_projection = accumulated + t * seg_length
            
            if d_perp < best_dist:
                best_dist = d_perp
                best_index = i
                best_accumulated = dist_to_projection
        
        # Acumular distancia del segmento
        seg_length = haversine_m(seg_start, seg_end)
        accumulated += seg_length
    
    return (best_index, best_accumulated)

def truncate_route_from_point(route: List[Tuple[float, float]], start_point: Tuple[float, float]) -> List[Tuple[float, float]]:
    """
    Trunca una ruta empezando desde un punto específico
    Encuentra el punto más cercano en la ruta y devuelve la ruta desde ahí hasta el final
    
    Args:
        route: Ruta completa [(lat, lon), ...]
        start_point: Punto desde donde empezar (lat, lon)
    
    Returns:
        Ruta truncada desde el punto más cercano hasta el final
    """
    if len(route) < 2:
        return route
    
    segment_index, accumulated_dist = find_point_on_route(route, start_point)
    
    # Si el punto está muy cerca del inicio, usar la ruta completa
    if accumulated_dist < 100.0:  # Menos de 100m desde el inicio
        return route
    
    # Si el punto está muy cerca del final, usar solo el último punto
    total_length = sum(haversine_m(route[i], route[i+1]) for i in range(len(route)-1))
    if accumulated_dist > total_length - 100.0:  # Menos de 100m hasta el final
        return [route[-1]]
    
    # Encontrar el punto exacto en el segmento
    seg_start = route[segment_index]
    seg_end = route[segment_index + 1]
    
    # Calcular el punto interpolado en el segmento
    lat0, lon0 = route[0]
    px, py = to_local_xy_m(lat0, lon0, start_point[0], start_point[1])
    ax, ay = to_local_xy_m(lat0, lon0, seg_start[0], seg_start[1])
    bx, by = to_local_xy_m(lat0, lon0, seg_end[0], seg_end[1])
    
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    ab2 = abx * abx + aby * aby
    
    if ab2 > 0:
        t = (apx * abx + apy * aby) / ab2
        t = max(0.0, min(1.0, t))
        
        # Interpolar coordenadas
        interp_lat = seg_start[0] + t * (seg_end[0] - seg_start[0])
        interp_lon = seg_start[1] + t * (seg_end[1] - seg_start[1])
        interp_point = (interp_lat, interp_lon)
        
        # Construir ruta truncada: punto interpolado + resto de la ruta
        truncated = [interp_point]
        truncated.extend(route[segment_index + 1:])
        
        return truncated
    
    # Fallback: usar desde el siguiente segmento
    return route[segment_index + 1:]

def route_to_geojson(route: List[Tuple[float, float]]) -> Dict:
    """
    Convierte una lista de puntos (lat, lon) a GeoJSON LineString (lon, lat)
    """
    coordinates = [[lon, lat] for lat, lon in route]
    return {
        'type': 'LineString',
        'coordinates': coordinates
    }

