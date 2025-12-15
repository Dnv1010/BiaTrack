"""
Parser para cargar datos de peajes desde formato Waze o estructurado
"""

import re
import json
from typing import List, Dict

def parse_waze_template(text: str) -> Dict:
    """
    Parsea un template de Waze en formato [wzTemplate topic=X post=Y][/wzTemplate]
    Retorna un diccionario con la información extraída
    """
    pattern = r'\[wzTemplate\s+topic=(\d+)\s+post=(\d+)\](.*?)\[/wzTemplate\]'
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        return {
            'topic': match.group(1),
            'post': match.group(2),
            'content': match.group(3).strip()
        }
    return None

def parse_toll_data_from_text(text: str) -> List[Dict]:
    """
    Parsea datos de peajes desde texto estructurado
    Formato esperado:
    - Nombre del peaje
    - Departamento
    - Operador (opcional)
    - Tarifa en COP
    - Estado (ACTIVE/REMOVED/SUSPENDED)
    """
    tolls = []
    lines = text.strip().split('\n')
    
    current_toll = None
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Detectar nombre del peaje (líneas que no tienen formato específico)
        if ':' not in line and not line.replace('.', '').replace(',', '').isdigit():
            if current_toll:
                tolls.append(current_toll)
            current_toll = {
                'name': line,
                'department': '',
                'operator': '',
                'fare_cop': 0,
                'status': 'ACTIVE'
            }
        elif ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            if current_toll:
                if 'departamento' in key or 'depto' in key:
                    current_toll['department'] = value
                elif 'operador' in key:
                    current_toll['operator'] = value
                elif 'tarifa' in key or 'precio' in key or 'costo' in key:
                    # Extraer número de la tarifa
                    fare_match = re.search(r'[\d.,]+', value.replace(',', ''))
                    if fare_match:
                        current_toll['fare_cop'] = int(float(fare_match.group().replace(',', '')))
                elif 'estado' in key or 'status' in key:
                    status_upper = value.upper()
                    if 'DESMONTADO' in status_upper or 'REMOVED' in status_upper:
                        current_toll['status'] = 'REMOVED'
                        current_toll['fare_cop'] = 0
                    elif 'SUSPENDIDO' in status_upper or 'SUSPENDED' in status_upper or 'SIN COBRO' in status_upper:
                        current_toll['status'] = 'SUSPENDED'
                        current_toll['fare_cop'] = 0
                    else:
                        current_toll['status'] = 'ACTIVE'
    
    if current_toll:
        tolls.append(current_toll)
    
    return tolls

def load_tolls_from_json(file_path: str) -> List[Dict]:
    """Carga peajes desde un archivo JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'tolls' in data:
                return data['tolls']
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []
    return []

def normalize_toll(toll: Dict, index: int = None) -> Dict:
    """
    Normaliza un diccionario de peaje al formato estándar
    """
    toll_id = toll.get('id') or f"toll-{index or hash(toll.get('name', ''))}"
    
    normalized = {
        'id': toll_id,
        'name': toll.get('name', toll.get('nombre', '')).strip(),
        'department': toll.get('department', toll.get('departamento', toll.get('depto', ''))).strip(),
        'operator': (toll.get('operator') or toll.get('operador') or '').strip() or None,
        'fare_cop': int(toll.get('fare_cop', toll.get('fareCOP', toll.get('tarifa', 0)))),
        'status': toll.get('status', 'ACTIVE').upper()
    }
    
    # Preservar coordenadas si existen
    if 'latitude' in toll:
        normalized['latitude'] = float(toll['latitude'])
    if 'longitude' in toll:
        normalized['longitude'] = float(toll['longitude'])
    
    return normalized

