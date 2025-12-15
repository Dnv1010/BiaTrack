"""
Servicio para calcular peajes en una ruta
Basado en la geometría de la ruta y ubicación de peajes
Usa proyección local para cálculos precisos de distancia
"""

from typing import List, Dict, Tuple, Set, Any, Optional
from data.tolls import TOLLS
import math
import requests
import time
import json

EARTH_R = 6371000.0  # Radio de la Tierra en metros


def haversine_m(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """
    Calcula distancia en metros entre dos puntos usando fórmula de Haversine
    """
    lat1, lon1 = a
    lat2, lon2 = b
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    s = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_R * math.asin(min(1.0, math.sqrt(s)))


def to_local_xy_m(lat0: float, lon0: float, lat: float, lon: float) -> Tuple[float, float]:
    """
    Convierte coordenadas geográficas a coordenadas locales XY (metros)
    usando proyección plana centrada en lat0, lon0
    """
    x = math.radians(lon - lon0) * EARTH_R * math.cos(math.radians(lat0))
    y = math.radians(lat - lat0) * EARTH_R
    return x, y


def point_segment_distance_m_xy(px, py, ax, ay, bx, by) -> float:
    """
    Calcula distancia de un punto a un segmento en coordenadas XY locales
    """
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    ab2 = abx * abx + aby * aby
    if ab2 == 0:
        return math.hypot(px - ax, py - ay)
    t = (apx * abx + apy * aby) / ab2
    t = max(0.0, min(1.0, t))
    cx, cy = ax + t * abx, ay + t * aby
    return math.hypot(px - cx, py - cy)


def polyline_length_m(route_latlon: List[Tuple[float, float]]) -> float:
    """
    Calcula la longitud total de una polilínea en metros
    """
    total = 0.0
    for i in range(len(route_latlon) - 1):
        total += haversine_m(route_latlon[i], route_latlon[i + 1])
    return total


def route_deviation_from_od_m(
    route_latlon: List[Tuple[float, float]],
    origin_latlon: Tuple[float, float],
    dest_latlon: Tuple[float, float],
) -> float:
    """
    Mide el máximo desvío (en metros) de la polilínea respecto al segmento OD (origen-destino),
    usando proyección local en metros.
    """
    lat0, lon0 = origin_latlon
    ox, oy = to_local_xy_m(lat0, lon0, origin_latlon[0], origin_latlon[1])
    dx, dy = to_local_xy_m(lat0, lon0, dest_latlon[0], dest_latlon[1])

    max_dev = 0.0
    for (lat, lon) in route_latlon:
        px, py = to_local_xy_m(lat0, lon0, lat, lon)
        d = point_segment_distance_m_xy(px, py, ox, oy, dx, dy)
        if d > max_dev:
            max_dev = d
    return max_dev


def pick_best_route_geometry(
    geometries: List[Dict[str, Any]],
    origin_latlon: Tuple[float, float],
    dest_latlon: Tuple[float, float],
) -> Dict[str, Any]:
    """
    Escoge la mejor ruta entre varias alternativas:
    Score = length_km + 0.7 * deviation_km + 5.0 * detour_ratio_penalty
    (penaliza rutas largas y rutas que se van fuera del corredor OD)
    """
    if not geometries:
        raise ValueError("No hay geometrías para elegir.")

    od_m = haversine_m(origin_latlon, dest_latlon)
    best = None
    best_score = float("inf")

    for g in geometries:
        route = route_from_linestring(g)
        length_m = polyline_length_m(route)
        dev_m = route_deviation_from_od_m(route, origin_latlon, dest_latlon)

        # ratio de rodeo vs distancia directa (si se va a Los Curos típicamente sube mucho)
        ratio = (length_m / od_m) if od_m > 0 else 999.0
        ratio_penalty = max(0.0, ratio - 1.25)  # empieza a penalizar a partir de 25% más largo

        score = (length_m / 1000.0) + 0.7 * (dev_m / 1000.0) + 5.0 * ratio_penalty

        if score < best_score:
            best_score = score
            best = g

    assert best is not None
    return best


def min_distance_point_to_polyline_m(point: Tuple[float, float], route: List[Tuple[float, float]]) -> Tuple[float, float]:
    """
    Calcula la distancia mínima de un punto a una polilínea (ruta)
    y la distancia acumulada desde el origen hasta el punto más cercano
    
    Args:
        point: Punto (lat, lon)
        route: Lista de puntos de la ruta [(lat, lon), ...]
    
    Returns:
        Tupla (distancia_perpendicular_m, distancia_acumulada_m)
        - distancia_perpendicular_m: Distancia perpendicular del punto a la ruta
        - distancia_acumulada_m: Distancia acumulada desde el origen hasta el punto más cercano en la ruta
    """
    if len(route) < 2:
        raise ValueError("La ruta debe tener al menos 2 puntos.")
    
    lat0, lon0 = route[0]
    px, py = to_local_xy_m(lat0, lon0, point[0], point[1])
    
    best_dist = float("inf")
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
                best_accumulated = dist_to_projection
        
        # Acumular distancia del segmento
        seg_length = haversine_m(seg_start, seg_end)
        accumulated += seg_length
    
    return (best_dist, best_accumulated)


def route_from_linestring(geometry: Dict[str, Any]) -> List[Tuple[float, float]]:
    """
    Convierte un GeoJSON LineString a lista de puntos (lat, lon)
    
    Args:
        geometry: GeoJSON LineString con formato {"type":"LineString","coordinates":[[lon,lat],...]}
    
    Returns:
        Lista de tuplas (lat, lon)
    """
    if geometry.get("type") != "LineString":
        raise ValueError("Se esperaba geometry.type == 'LineString'")
    coords = geometry.get("coordinates")
    if not isinstance(coords, list) or len(coords) < 2:
        raise ValueError("LineString.coordinates inválido o con <2 puntos")
    out: List[Tuple[float, float]] = []
    for c in coords:
        if isinstance(c, list) and len(c) >= 2:
            lon, lat = c[0], c[1]
            if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                out.append((float(lat), float(lon)))
    if len(out) < 2:
        raise ValueError("No se pudo construir ruta (lat,lon) desde coordinates")
    return out


def toll_point_from_feature(feature: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    """
    Extrae las coordenadas de un peaje desde un feature GeoJSON
    Soporta geometry Point y propiedades latsig/longsig
    """
    geom = feature.get("geometry")
    if geom and geom.get("type") == "Point":
        coords = geom.get("coordinates")
        if isinstance(coords, list) and len(coords) >= 2:
            lon, lat = coords[0], coords[1]  # GeoJSON = [lon,lat]
            if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                return (float(lat), float(lon))

    props = feature.get("properties") or {}
    lat = props.get("latsig") or props.get("latitud")
    lon = props.get("longsig") or props.get("longitud")
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        # Verificar que no sean el mismo valor (error común en los datos)
        if lat != lon:
            return (float(lat), float(lon))
    return None

def _calcular_peajes(
    geometry: Dict,
    tolls_db: List[Dict] = None,
    threshold_m: float = 5000.0,
    origin_latlon: Optional[Tuple[float, float]] = None,
    dest_latlon: Optional[Tuple[float, float]] = None
) -> Dict:
    """
    Calcula qué peajes están en la ruta basándose en la geometría
    Ordena los peajes según su posición en la ruta (distancia acumulada desde el origen)
    Solo incluye peajes que están en el orden lógico de la ruta (desde origen hasta destino)
    
    Args:
        geometry: GeoJSON LineString con la ruta
        tolls_db: Lista de peajes (default: TOLLS)
        threshold_m: Umbral de distancia en metros (default: 5000m = 5km)
        origin_latlon: Coordenadas del origen (lat, lon) - opcional, para validación
        dest_latlon: Coordenadas del destino (lat, lon) - opcional, para validación
    
    Returns:
        dict con 'peajes_en_ruta', 'costo_total_cop', 'count'
    """
    if tolls_db is None:
        tolls_db = TOLLS
    
    if not geometry or geometry.get('type') != 'LineString':
        return {
            'peajes_en_ruta': [],
            'costo_total_cop': 0,
            'count': 0
        }
    
    try:
        # Convertir GeoJSON LineString a lista de puntos (lat, lon)
        route = route_from_linestring(geometry)
    except (ValueError, KeyError, TypeError) as e:
        print(f"[ERROR] Error procesando geometría de ruta: {e}")
        return {
            'peajes_en_ruta': [],
            'costo_total_cop': 0,
            'count': 0
        }
    
    # Calcular distancia total de la ruta para validación
    route_length_m = polyline_length_m(route)
    
    peajes_en_ruta = []
    
    # SOLO incluir peajes que tienen coordenadas y están cerca de la ruta
    for toll in tolls_db:
        # Solo considerar peajes activos
        if toll.get('status') != 'ACTIVE':
            continue
        
        # SOLO procesar peajes con coordenadas
        if 'latitude' in toll and 'longitude' in toll:
            try:
                toll_lat = float(toll['latitude'])
                toll_lon = float(toll['longitude'])
                toll_point = (toll_lat, toll_lon)
                
                # Calcular distancia perpendicular y posición en la ruta
                d_perp_m, d_accumulated_m = min_distance_point_to_polyline_m(toll_point, route)
                
                # Solo incluir si está cerca de la ruta (umbral más estricto)
                if d_perp_m <= threshold_m:
                    # Validar que el peaje esté dentro del rango de la ruta
                    # Solo incluir peajes que están entre el origen y el destino
                    margin_start = 1000.0  # 1km desde el origen (evita peajes en el punto de partida)
                    margin_end = 200.0  # 200m al final (ajustado para incluir La Lizama que está muy cerca del destino)
                    
                    # Validación básica: el peaje debe estar dentro del rango de la ruta
                    if margin_start <= d_accumulated_m <= route_length_m - margin_end:
                        # Validación adicional: verificar que el peaje esté en la dirección correcta
                        is_valid = True
                        
                        if origin_latlon and dest_latlon:
                            # Calcular distancia del peaje al origen y destino en línea recta
                            dist_to_origin_straight = haversine_m((toll_lat, toll_lon), origin_latlon)
                            dist_to_dest_straight = haversine_m((toll_lat, toll_lon), dest_latlon)
                            od_distance_straight = haversine_m(origin_latlon, dest_latlon)
                            
                            # El peaje debe estar progresando hacia el destino
                            progress_ratio = d_accumulated_m / route_length_m if route_length_m > 0 else 0
                            
                            # Validación 1: El peaje debe estar al menos a 1km del origen
                            if d_accumulated_m < margin_start:
                                is_valid = False
                            
                            # Validación 2: Verificar que el peaje esté en la dirección general correcta usando producto escalar
                            # Calcular el vector desde el origen hasta el destino y desde el origen hasta el peaje
                            lat0, lon0 = origin_latlon
                            latd, lond = dest_latlon
                            
                            # Vector OD (origen -> destino)
                            dx_od = lond - lon0
                            dy_od = latd - lat0
                            
                            # Vector origen -> peaje
                            dx_toll = toll_lon - lon0
                            dy_toll = toll_lat - lat0
                            
                            # Producto escalar para verificar dirección
                            dot_product = dx_od * dx_toll + dy_od * dy_toll
                            
                            # Si el producto escalar es negativo, el peaje está en dirección opuesta
                            if dot_product <= 0:
                                is_valid = False
                            
                            # Validación 3: El peaje debe estar progresando hacia el destino
                            # Calcular el ratio de progreso en la ruta
                            progress_ratio = d_accumulated_m / route_length_m if route_length_m > 0 else 0
                            
                            # Si el peaje está muy cerca del origen (< 7km) pero está después del 8% de la ruta,
                            # probablemente está en otra carretera (como Los Curos que está en dirección San Gil)
                            if dist_to_origin_straight < 7000.0 and progress_ratio > 0.08:
                                # El peaje está muy cerca del origen pero avanzado en la ruta = otra carretera
                                is_valid = False
                            
                            # Si está después del 20% de la ruta, debe estar más cerca del destino que del origen
                            # (ajustado para permitir peajes como Lebrija que están al inicio pero en la dirección correcta)
                            if progress_ratio > 0.20:
                                if dist_to_dest_straight >= dist_to_origin_straight:
                                    # Si el peaje está más cerca del origen que del destino después del 20%, está en dirección opuesta
                                    is_valid = False
                            
                            # Validación 4: El peaje debe estar dentro del 99.9% de la ruta (ajustado para incluir peajes cerca del destino como La Lizama)
                            # Esta validación es redundante con el margen final, pero la mantenemos como seguridad adicional
                            if d_accumulated_m > route_length_m * 0.999:
                                is_valid = False
                        
                        if is_valid:
                            peajes_en_ruta.append({
                                'id': toll.get('id'),
                                'name': toll.get('name'),
                                'fare_cop': toll.get('fare_cop', 0),
                                'department': toll.get('department'),
                                'operator': toll.get('operator'),
                                'latitude': toll_lat,
                                'longitude': toll_lon,
                                'distance_from_route_km': round(d_perp_m / 1000.0, 3),  # Distancia perpendicular
                                'position_along_route_km': round(d_accumulated_m / 1000.0, 3)  # Posición en la ruta
                            })
            except (ValueError, TypeError, KeyError) as e:
                # Si hay error procesando este peaje, continuar con el siguiente
                continue
    
    # Ordenar por posición en la ruta (distancia acumulada desde el origen)
    peajes_en_ruta.sort(key=lambda x: x['position_along_route_km'])
    
    costo_total = sum(p['fare_cop'] for p in peajes_en_ruta)
    
    return {
        'peajes_en_ruta': peajes_en_ruta,
        'costo_total_cop': int(costo_total),
        'count': len(peajes_en_ruta)
    }

def _detectar_departamentos_en_ruta(ruta_coords: List[List[float]], max_points: int = 10) -> Set[str]:
    """
    Detecta qué departamentos atraviesa la ruta usando geocoding inverso
    en puntos clave de la ruta
    
    Args:
        ruta_coords: Lista de coordenadas [lat, lon] de la ruta
        max_points: Número máximo de puntos a verificar
    
    Returns:
        Set con nombres de departamentos (en mayúsculas)
    """
    departments = set()
    
    # Seleccionar puntos distribuidos a lo largo de la ruta
    if len(ruta_coords) <= max_points:
        points_to_check = ruta_coords
    else:
        step = len(ruta_coords) // max_points
        points_to_check = [ruta_coords[i] for i in range(0, len(ruta_coords), step)]
    
    for lat, lon in points_to_check[:max_points]:
        try:
            # Geocoding inverso usando Nominatim
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1
            }
            headers = {'User-Agent': 'BiaTrack/1.0'}
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})
                
                # Buscar departamento en diferentes campos
                dept = (
                    address.get('state') or 
                    address.get('region') or 
                    address.get('county') or
                    ''
                ).upper()
                
                if dept:
                    # Normalizar nombres de departamentos colombianos
                    dept_normalized = _normalizar_departamento(dept)
                    if dept_normalized:
                        departments.add(dept_normalized)
            
            time.sleep(1)  # Rate limiting de Nominatim
        except Exception:
            continue
    
    return departments

def _normalizar_departamento(dept: str) -> str:
    """
    Normaliza nombres de departamentos a formato estándar
    """
    dept = dept.upper().strip()
    
    # Mapeo de variaciones comunes
    mapping = {
        'ANTIOQUIA': 'ANTIOQUIA',
        'ATLANTICO': 'ATLÁNTICO',
        'ATLÁNTICO': 'ATLÁNTICO',
        'BOLIVAR': 'BOLÍVAR',
        'BOLÍVAR': 'BOLÍVAR',
        'BOYACA': 'BOYACÁ',
        'BOYACÁ': 'BOYACÁ',
        'CALDAS': 'CALDAS',
        'CASANARE': 'CASANARE',
        'CAUCA': 'CAUCA',
        'CESAR': 'CESAR',
        'CORDOBA': 'CÓRDOBA',
        'CÓRDOBA': 'CÓRDOBA',
        'CUNDINAMARCA': 'CUNDINAMARCA',
        'HUILA': 'HUILA',
        'LA GUAJIRA': 'LA GUAJIRA',
        'MAGDALENA': 'MAGDALENA',
        'META': 'META',
        'NARIÑO': 'NARIÑO',
        'NARINO': 'NARIÑO',
        'NORTE DE SANTANDER': 'NORTE DE SANTANDER',
        'QUINDIO': 'QUINDÍO',
        'QUINDÍO': 'QUINDÍO',
        'RISARALDA': 'RISARALDA',
        'SANTANDER': 'SANTANDER',
        'SUCRE': 'SUCRE',
        'TOLIMA': 'TOLIMA',
        'VALLE DEL CAUCA': 'VALLE DEL CAUCA',
        'VALLE': 'VALLE DEL CAUCA',
    }
    
    return mapping.get(dept, dept)

