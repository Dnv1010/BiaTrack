"""
BiaTrack - Calculadora de Traslados para Colombia
Aplicación Flask que calcula costos de traslados basándose en datos de base de datos
"""

from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
import sqlite3
import csv
import io
import os
import json
from typing import Optional, Dict, List
from data.contractors import CONTRACTORS
from data.tolls import TOLLS
from services.geocoding import geocode_city, buscar_ciudad
from services.routing import calcular_ruta_con_trafico, calcular_ruta_inversa
from services.toll_calculator import _calcular_peajes

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static',
            static_url_path='/static')
app.config['SECRET_KEY'] = 'biatrack-secret-key-2024'

DEFAULT_KM_PER_GALLON = 30  # Valor por defecto para vehículos livianos (Categoría I)

# Base de datos
# En Vercel, usar /tmp para escritura; en local usar archivo normal
DB_FILE = os.environ.get('DB_FILE') or (os.path.join('/tmp', 'biatrack.db') if os.path.exists('/tmp') else 'biatrack.db')

def init_db():
    """Inicializa la base de datos SQLite"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            contractor_name TEXT NOT NULL,
            base_label TEXT NOT NULL,
            origin_city TEXT NOT NULL,
            destination_text TEXT NOT NULL,
            fuel_type TEXT NOT NULL,
            fuel_price_per_gallon_cop REAL NOT NULL,
            km_per_gallon REAL NOT NULL,
            one_way_distance_km REAL NOT NULL,
            round_trip_distance_km REAL NOT NULL,
            one_way_eta_minutes INTEGER NOT NULL,
            peak_eta_minutes INTEGER NOT NULL,
            toll_count_one_way INTEGER NOT NULL,
            toll_cost_one_way_cop INTEGER NOT NULL,
            toll_count_round_trip INTEGER NOT NULL,
            toll_cost_round_trip_cop INTEGER NOT NULL,
            fuel_gallons_one_way REAL NOT NULL,
            fuel_gallons_round_trip REAL NOT NULL,
            fuel_cost_round_trip_cop INTEGER NOT NULL,
            total_round_trip_cop INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def compute_trip_result(data: Dict) -> Dict:
    """
    Calcula el resultado del viaje completo
    """
    # Calcular valores derivados
    round_trip_distance_km = data['one_way_distance_km'] * 2
    peak_eta_minutes = round(data['one_way_eta_minutes'] * 3.5)
    
    # Calcular combustible
    fuel_gallons_one_way = data['one_way_distance_km'] / data['km_per_gallon']
    fuel_gallons_round_trip = fuel_gallons_one_way * 2
    fuel_cost_round_trip_cop = round(fuel_gallons_round_trip * data['fuel_price_per_gallon_cop'])
    
    # Calcular peajes (ya viene calculado desde el frontend)
    toll_cost_round_trip_cop = data['toll_cost_one_way_cop'] * 2
    toll_count_round_trip = data['toll_count_one_way'] * 2
    
    # Total
    total_round_trip_cop = fuel_cost_round_trip_cop + toll_cost_round_trip_cop
    
    return {
        'id': data.get('id', f"trip_{datetime.now().timestamp()}"),
        'created_at': data.get('created_at', datetime.now().isoformat()),
        'contractor_name': data['contractor_name'],
        'base_label': data['base_label'],
        'origin_city': data['origin_city'],
        'destination_text': data['destination_text'],
        'fuel_type': data['fuel_type'],
        'fuel_price_per_gallon_cop': data['fuel_price_per_gallon_cop'],
        'km_per_gallon': data['km_per_gallon'],
        'one_way_distance_km': data['one_way_distance_km'],
        'round_trip_distance_km': round_trip_distance_km,
        'one_way_eta_minutes': data['one_way_eta_minutes'],
        'peak_eta_minutes': peak_eta_minutes,
        'toll_count_one_way': data['toll_count_one_way'],
        'toll_cost_one_way_cop': data['toll_cost_one_way_cop'],
        'toll_count_round_trip': toll_count_round_trip,
        'toll_cost_round_trip_cop': toll_cost_round_trip_cop,
        'fuel_gallons_one_way': round(fuel_gallons_one_way, 3),
        'fuel_gallons_round_trip': round(fuel_gallons_round_trip, 3),
        'fuel_cost_round_trip_cop': fuel_cost_round_trip_cop,
        'total_round_trip_cop': total_round_trip_cop
    }

def save_trip(trip: Dict):
    """Guarda un viaje en la base de datos"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trips (
            id, created_at, contractor_name, base_label, origin_city, destination_text,
            fuel_type, fuel_price_per_gallon_cop, km_per_gallon,
            one_way_distance_km, round_trip_distance_km,
            one_way_eta_minutes, peak_eta_minutes,
            toll_count_one_way, toll_cost_one_way_cop,
            toll_count_round_trip, toll_cost_round_trip_cop,
            fuel_gallons_one_way, fuel_gallons_round_trip, fuel_cost_round_trip_cop,
            total_round_trip_cop
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        trip['id'], trip['created_at'], trip['contractor_name'], trip['base_label'],
        trip['origin_city'], trip['destination_text'], trip['fuel_type'],
        trip['fuel_price_per_gallon_cop'], trip['km_per_gallon'],
        trip['one_way_distance_km'], trip['round_trip_distance_km'],
        trip['one_way_eta_minutes'], trip['peak_eta_minutes'],
        trip['toll_count_one_way'], trip['toll_cost_one_way_cop'],
        trip['toll_count_round_trip'], trip['toll_cost_round_trip_cop'],
        trip['fuel_gallons_one_way'], trip['fuel_gallons_round_trip'],
        trip['fuel_cost_round_trip_cop'], trip['total_round_trip_cop']
    ))
    conn.commit()
    conn.close()

def get_all_trips() -> List[Dict]:
    """Obtiene todos los viajes de la base de datos"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trips ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_trip(trip_id: str):
    """Elimina un viaje de la base de datos"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM trips WHERE id = ?', (trip_id,))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Página principal"""
    trips = get_all_trips()
    return render_template('index.html', 
                         trips=trips, 
                         contractors=CONTRACTORS,
                         default_km_per_gallon=DEFAULT_KM_PER_GALLON)


@app.route('/api/trip', methods=['POST'])
def create_trip():
    """API endpoint para crear un nuevo viaje"""
    data = request.json
    
    # Validaciones básicas
    required_fields = [
        'contractor_name', 'base_label', 'origin_city', 'destination_text',
        'fuel_type', 'fuel_price_per_gallon_cop', 'km_per_gallon',
        'one_way_distance_km', 'one_way_eta_minutes',
        'toll_count_one_way', 'toll_cost_one_way_cop'
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'Campo requerido faltante: {field}'}), 400
    
    # Generar ID y timestamp
    trip_data = data.copy()
    trip_data['id'] = f"trip_{datetime.now().timestamp()}_{hash(str(data))}"
    trip_data['created_at'] = datetime.now().isoformat()
    
    # Calcular resultado
    trip_result = compute_trip_result(trip_data)
    
    # Guardar en base de datos
    save_trip(trip_result)
    
    return jsonify({'success': True, 'trip': trip_result})

@app.route('/api/trip/<trip_id>', methods=['DELETE'])
def delete_trip_endpoint(trip_id):
    """API endpoint para eliminar un viaje"""
    delete_trip(trip_id)
    return jsonify({'success': True})

@app.route('/api/tolls', methods=['GET'])
def get_tolls():
    """API endpoint para obtener todos los peajes"""
    return jsonify({'success': True, 'tolls': TOLLS})

@app.route('/api/tolls/load', methods=['POST'])
def load_tolls_from_text():
    """API endpoint para cargar peajes desde texto"""
    from data.tolls_parser import parse_toll_data_from_text, parse_waze_template, normalize_toll
    
    data = request.json
    text = data.get('text', '').strip()
    format_type = data.get('format', 'text')  # 'text' o 'waze'
    
    try:
        if format_type == 'waze':
            template_data = parse_waze_template(text)
            if template_data:
                text = template_data['content']
            else:
                return jsonify({'success': False, 'error': 'No se encontró un template Waze válido'}), 400
        
        tolls = parse_toll_data_from_text(text)
        if not tolls:
            return jsonify({'success': False, 'error': 'No se encontraron peajes en el texto'}), 400
        
        normalized_tolls = [normalize_toll(toll, i) for i, toll in enumerate(tolls)]
        
        # Guardar en archivo JSON
        import json
        json_path = os.path.join('data', 'tolls_data.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(normalized_tolls, f, ensure_ascii=False, indent=2)
        
        # Recargar peajes
        from data.tolls import load_tolls
        global TOLLS
        TOLLS = load_tolls()
        
        return jsonify({
            'success': True,
            'message': f'Se cargaron {len(normalized_tolls)} peajes correctamente',
            'tolls': normalized_tolls
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/buscar_ciudad', methods=['GET'])
def buscar_ciudad_endpoint():
    """API endpoint para autocompletar ciudades"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'success': True, 'ciudades': []})
    
    ciudades = buscar_ciudad(query)
    return jsonify({'success': True, 'ciudades': ciudades})

@app.route('/api/calcular_ruta_supply', methods=['GET'])
def calcular_ruta_supply():
    """
    Calcula ruta con distancia, tiempos, costos y peajes
    Según el diagrama de flujo proporcionado
    """
    try:
        # Obtener parámetros
        origin = request.args.get('origin', '').strip()
        destination = request.args.get('destination', '').strip()
        km_per_liter = float(request.args.get('km_per_liter', DEFAULT_KM_PER_GALLON))
        precio_liter_cop = float(request.args.get('precio_liter_cop', 0))
        round_trip = request.args.get('round_trip', 'false').lower() == 'true'
        
        print(f"[DEBUG] Calculando ruta: {origin} -> {destination}")
        print(f"[DEBUG] Parámetros: km_per_liter={km_per_liter}, precio_liter_cop={precio_liter_cop}, round_trip={round_trip}")
        
        if not origin or not destination:
            return jsonify({'success': False, 'error': 'Origen y destino son requeridos'}), 400
        
        if km_per_liter <= 0:
            return jsonify({'success': False, 'error': 'Rendimiento (km por litro) debe ser mayor a 0'}), 400
        
        if precio_liter_cop <= 0:
            return jsonify({'success': False, 'error': 'Precio por litro debe ser mayor a 0'}), 400
        
        # Geocodificar ciudades
        print(f"[DEBUG] Geocodificando origen: {origin}")
        origin_coords = geocode_city(origin)
        print(f"[DEBUG] Coordenadas origen: {origin_coords}")
        
        print(f"[DEBUG] Geocodificando destino: {destination}")
        dest_coords = geocode_city(destination)
        print(f"[DEBUG] Coordenadas destino: {dest_coords}")
        
        if not origin_coords or not dest_coords:
            return jsonify({
                'success': False, 
                'error': f'No se pudieron encontrar coordenadas para {"origen" if not origin_coords else "destino"}'
            }), 400
        
        # Calcular ruta ida
        print(f"[DEBUG] Calculando ruta con OSRM...")
        route_ida = calcular_ruta_con_trafico(
            origin_coords['lat'],
            origin_coords['lon'],
            dest_coords['lat'],
            dest_coords['lon']
        )
        print(f"[DEBUG] Ruta calculada: {route_ida is not None}")
        
        if not route_ida:
            return jsonify({'success': False, 'error': 'No se pudo calcular la ruta. Verifica que las ciudades existan.'}), 400
        
        # Calcular peajes en ruta ida (ruta completa desde origen)
        origin_latlon = (origin_coords['lat'], origin_coords['lon'])
        dest_latlon = (dest_coords['lat'], dest_coords['lon'])
        peajes_ida_completa = _calcular_peajes(
            route_ida.get('geometry'),
            threshold_m=1000.0,  # 1km para capturar peajes cercanos pero con validación estricta de dirección
            origin_latlon=origin_latlon,
            dest_latlon=dest_latlon
        )
        
        # Identificar el primer peaje y recalcular ruta desde ahí
        primer_peaje = None
        ruta_desde_primer_peaje = route_ida.get('geometry')
        distancia_desde_primer_peaje_km = route_ida['distance_km']
        
        if peajes_ida_completa['count'] > 0:
            # Ordenar peajes por posición en la ruta (ya están ordenados)
            peajes_ordenados = peajes_ida_completa['peajes_en_ruta']
            primer_peaje = peajes_ordenados[0]
            
            # Truncar la ruta desde el primer peaje
            from services.route_utils import truncate_route_from_point, route_to_geojson, polyline_length_m
            from services.toll_calculator import route_from_linestring
            
            ruta_completa = route_from_linestring(route_ida.get('geometry'))
            primer_peaje_point = (primer_peaje['latitude'], primer_peaje['longitude'])
            ruta_truncada = truncate_route_from_point(ruta_completa, primer_peaje_point)
            
            # Convertir de vuelta a GeoJSON
            ruta_desde_primer_peaje = route_to_geojson(ruta_truncada)
            
            # Calcular distancia desde el primer peaje
            distancia_desde_primer_peaje_km = round(polyline_length_m(ruta_truncada) / 1000.0, 2)
            
            # Recalcular peajes en la ruta truncada (desde primer peaje hasta destino)
            peajes_ida = _calcular_peajes(
                ruta_desde_primer_peaje,
                threshold_m=1000.0,
                origin_latlon=primer_peaje_point,
                dest_latlon=dest_latlon
            )
            
            # IMPORTANTE: Incluir el costo del primer peaje (peaje de salida) en el total
            # El primer peaje debe pagarse aunque la distancia se calcule desde ahí
            costo_primer_peaje = primer_peaje.get('fare_cop', 0)
            peajes_ida['costo_total_cop'] = peajes_ida['costo_total_cop'] + costo_primer_peaje
            peajes_ida['count'] = peajes_ida['count'] + 1
            
            # Agregar el primer peaje al inicio de la lista de peajes para mostrarlo
            primer_peaje_con_posicion = {
                **primer_peaje,
                'position_along_route_km': 0.0,  # Está al inicio de la ruta calculada
                'distance_from_route_km': 0.0,  # Está exactamente en la ruta
                'is_exit_toll': True  # Marcar como peaje de salida
            }
            peajes_ida['peajes_en_ruta'].insert(0, primer_peaje_con_posicion)
            
            print(f"[DEBUG] Primer peaje: {primer_peaje['name']} en posición {primer_peaje['position_along_route_km']:.2f} km")
            print(f"[DEBUG] Costo primer peaje: ${costo_primer_peaje:,} COP")
            print(f"[DEBUG] Distancia desde primer peaje: {distancia_desde_primer_peaje_km} km")
            print(f"[DEBUG] Costo total peajes (incluyendo primer peaje): ${peajes_ida['costo_total_cop']:,} COP")
        else:
            # No hay peajes, usar ruta completa
            peajes_ida = peajes_ida_completa
            ruta_desde_primer_peaje = route_ida.get('geometry')
            distancia_desde_primer_peaje_km = route_ida['distance_km']
            print(f"[DEBUG] No se encontraron peajes, usando ruta completa")
        
        # Calcular costos ida (desde primer peaje o desde origen si no hay peajes)
        distancia_ida_km = distancia_desde_primer_peaje_km
        litros_ida = distancia_ida_km / km_per_liter
        costo_combustible_ida = litros_ida * precio_liter_cop
        
        resultado = {
            'success': True,
            'ida': {
                'origin': {
                    'name': origin,
                    'lat': origin_coords['lat'],
                    'lon': origin_coords['lon'],
                    'display_name': origin_coords.get('display_name', origin)
                },
                'destination': {
                    'name': destination,
                    'lat': dest_coords['lat'],
                    'lon': dest_coords['lon'],
                    'display_name': dest_coords.get('display_name', destination)
                },
                'first_toll': primer_peaje if primer_peaje else None,
                'distance_km': distancia_ida_km,
                'distance_from_origin_km': route_ida['distance_km'] if primer_peaje else None,
                'duration_normal_min': route_ida['duration_normal_min'],
                'duration_peak_min': route_ida['duration_peak_min'],
                'geometry': ruta_desde_primer_peaje,
                'geometry_full': route_ida.get('geometry'),
                'peajes': peajes_ida,
                'combustible': {
                    'liters': round(litros_ida, 2),
                    'cost_cop': int(costo_combustible_ida)
                },
                'total_cost_cop': int(costo_combustible_ida + peajes_ida['costo_total_cop'])
            }
        }
        
        # Si es ida y regreso, calcular ruta de regreso
        if round_trip:
            route_regreso = calcular_ruta_inversa(
                origin_coords['lat'],
                origin_coords['lon'],
                dest_coords['lat'],
                dest_coords['lon']
            )
            
            if route_regreso:
                # Para la ruta de regreso, invertir origen y destino
                peajes_regreso = _calcular_peajes(
                    route_regreso.get('geometry'),
                    threshold_m=1000.0,  # 1km para capturar peajes cercanos pero con validación estricta de dirección
                    origin_latlon=dest_latlon,  # El destino se convierte en origen
                    dest_latlon=origin_latlon   # El origen se convierte en destino
                )
                distancia_regreso_km = route_regreso['distance_km']
                litros_regreso = distancia_regreso_km / km_per_liter
                costo_combustible_regreso = litros_regreso * precio_liter_cop
                
                resultado['regreso'] = {
                    'distance_km': distancia_regreso_km,
                    'duration_normal_min': route_regreso['duration_normal_min'],
                    'duration_peak_min': route_regreso['duration_peak_min'],
                    'geometry': route_regreso.get('geometry'),
                    'peajes': peajes_regreso,
                    'combustible': {
                        'liters': round(litros_regreso, 2),
                        'cost_cop': int(costo_combustible_regreso)
                    },
                    'total_cost_cop': int(costo_combustible_regreso + peajes_regreso['costo_total_cop'])
                }
                
                # Totales ida y regreso (ruta de regreso exitosa)
                resultado['total'] = {
                    'distance_km': distancia_ida_km + distancia_regreso_km,
                    'combustible_liters': round(litros_ida + litros_regreso, 2),
                    'combustible_cost_cop': int(costo_combustible_ida + costo_combustible_regreso),
                    'peajes_cost_cop': peajes_ida['costo_total_cop'] + peajes_regreso['costo_total_cop'],
                    'peajes_count': peajes_ida['count'] + peajes_regreso['count'],
                    'total_cost_cop': int(costo_combustible_ida + costo_combustible_regreso + 
                                         peajes_ida['costo_total_cop'] + peajes_regreso['costo_total_cop'])
                }
            else:
                # Ruta de regreso falló, pero aún así crear total con solo datos de ida
                # (duplicando la ida como aproximación)
                resultado['regreso'] = None
                resultado['total'] = {
                    'distance_km': distancia_ida_km * 2,  # Aproximación: duplicar distancia de ida
                    'combustible_liters': round(litros_ida * 2, 2),
                    'combustible_cost_cop': int(costo_combustible_ida * 2),
                    'peajes_cost_cop': peajes_ida['costo_total_cop'] * 2,  # Aproximación: duplicar peajes de ida
                    'peajes_count': peajes_ida['count'] * 2,
                    'total_cost_cop': int((costo_combustible_ida + peajes_ida['costo_total_cop']) * 2),
                    'warning': 'No se pudo calcular la ruta de regreso. Los totales son aproximados (duplicando la ida).'
                }
        
        return jsonify(resultado)
        
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Error en parámetros: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error al calcular ruta: {str(e)}'}), 500

@app.route('/api/trips/export', methods=['GET'])
def export_trips():
    """Exporta todos los viajes a CSV"""
    trips = get_all_trips()
    
    if not trips:
        return jsonify({'error': 'No hay viajes para exportar'}), 404
    
    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=trips[0].keys())
    writer.writeheader()
    writer.writerows(trips)
    
    # Crear respuesta
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'biatrack_trips_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

# Inicializar base de datos solo si no estamos en Vercel
# En Vercel, la inicialización se hace de forma lazy
if __name__ == '__main__':
    init_db()
    print("=" * 60)
    print("BiaTrack - Calculadora de Traslados")
    print("=" * 60)
    print(f"Servidor iniciando en http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # En Vercel/serverless, inicializar DB de forma lazy
    # La DB se inicializará en la primera request
    pass
