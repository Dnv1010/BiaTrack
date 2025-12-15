"""
Datos hardcoded de peajes en Colombia
Carga datos desde archivos o estructura directa
"""

import os
from .tolls_parser import parse_toll_data_from_text, load_tolls_from_json, normalize_toll

# Peajes hardcoded - estructura directa
HARDCODED_TOLLS = [
    # Agregar peajes aquí en formato:
    # {
    #     "id": "toll-1",
    #     "name": "Nombre del Peaje",
    #     "department": "Departamento",
    #     "operator": "Operador (opcional)",
    #     "fare_cop": 15000,
    #     "status": "ACTIVE"  # ACTIVE, REMOVED, o SUSPENDED
    # },
]

def load_tolls() -> list:
    """
    Carga todos los peajes desde múltiples fuentes:
    1. Peajes hardcoded
    2. Archivo JSON (tolls_data.json)
    3. Archivo de texto (tolls_data.txt)
    """
    all_tolls = []
    
    # 1. Cargar peajes hardcoded
    for i, toll in enumerate(HARDCODED_TOLLS):
        all_tolls.append(normalize_toll(toll, i))
    
    # 2. Intentar cargar desde JSON
    json_path = os.path.join(os.path.dirname(__file__), 'tolls_data.json')
    json_tolls = load_tolls_from_json(json_path)
    for i, toll in enumerate(json_tolls, start=len(all_tolls)):
        all_tolls.append(normalize_toll(toll, i))
    
    # 3. Intentar cargar desde texto
    txt_path = os.path.join(os.path.dirname(__file__), 'tolls_data.txt')
    if os.path.exists(txt_path):
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
                if text_content.strip() and not text_content.strip().startswith('#'):
                    text_tolls = parse_toll_data_from_text(text_content)
                    for i, toll in enumerate(text_tolls, start=len(all_tolls)):
                        all_tolls.append(normalize_toll(toll, i))
        except Exception:
            pass
    
    return all_tolls

# Cargar peajes al importar el módulo
TOLLS = load_tolls()
