"""
Lógica de cálculo de costos de traslado
"""

import uuid
from datetime import datetime

DEFAULT_KM_PER_GALLON = 30

def compute_trip_result(input_data: dict, contractors: list, tolls: list) -> dict:
    """
    Calcula el resultado completo de un viaje
    
    Args:
        input_data: Datos del viaje
        contractors: Lista de contratistas
        tolls: Lista de peajes
    
    Returns:
        dict: Resultado completo del cálculo
    """
    # Buscar contratista y base
    contractor = next((c for c in contractors if c['id'] == input_data['contractorId']), None)
    base = None
    if contractor:
        base = next((b for b in contractor['bases'] if b['id'] == input_data['baseId']), None)
    
    # Calcular peajes
    selected_toll_ids = input_data.get('selectedTollIds', [])
    selected_tolls = [t for t in tolls if t['id'] in selected_toll_ids]
    
    toll_cost_one_way_cop = round(sum(t.get('fareCOP', 0) for t in selected_tolls))
    toll_count_one_way = len(selected_tolls)
    toll_cost_round_trip_cop = toll_cost_one_way_cop * 2
    toll_count_round_trip = toll_count_one_way * 2
    
    # Calcular distancias y tiempos
    one_way_distance_km = float(input_data['oneWayDistanceKm'])
    round_trip_distance_km = one_way_distance_km * 2
    one_way_eta_minutes = int(input_data['oneWayEtaMinutes'])
    peak_eta_minutes = round(one_way_eta_minutes * 3.5)
    
    # Calcular combustible
    km_per_gallon = float(input_data['kmPerGallon'])
    fuel_gallons_one_way = one_way_distance_km / km_per_gallon
    fuel_gallons_round_trip = fuel_gallons_one_way * 2
    fuel_price_per_gallon_cop = float(input_data['fuelPricePerGallonCOP'])
    fuel_cost_round_trip_cop = round(fuel_gallons_round_trip * fuel_price_per_gallon_cop)
    
    # Total
    total_round_trip_cop = fuel_cost_round_trip_cop + toll_cost_round_trip_cop
    
    # Crear resultado
    result = {
        'id': str(uuid.uuid4()),
        'createdAtISO': datetime.now().isoformat(),
        'contractorName': contractor['name'] if contractor else 'Contratista',
        'baseLabel': base['label'] if base else 'Base',
        'originCity': input_data['originCity'],
        'destinationText': input_data['destinationText'],
        'fuelType': input_data['fuelType'],
        'fuelPricePerGallonCOP': fuel_price_per_gallon_cop,
        'kmPerGallon': km_per_gallon,
        'oneWayDistanceKm': one_way_distance_km,
        'roundTripDistanceKm': round_trip_distance_km,
        'oneWayEtaMinutes': one_way_eta_minutes,
        'peakEtaMinutes': peak_eta_minutes,
        'tollCountOneWay': toll_count_one_way,
        'tollCostOneWayCOP': toll_cost_one_way_cop,
        'tollCountRoundTrip': toll_count_round_trip,
        'tollCostRoundTripCOP': toll_cost_round_trip_cop,
        'fuelGallonsOneWay': round(fuel_gallons_one_way, 3),
        'fuelGallonsRoundTrip': round(fuel_gallons_round_trip, 3),
        'fuelCostRoundTripCOP': fuel_cost_round_trip_cop,
        'totalRoundTripCOP': total_round_trip_cop,
    }
    
    return result

