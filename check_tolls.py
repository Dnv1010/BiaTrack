"""Script para verificar estadísticas de peajes"""

import json
from data.tolls import TOLLS

import sys
import io

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("ESTADISTICAS DE PEAJES - BiaTrack")
print("=" * 60)

# Estadísticas desde TOLLS (cargado en memoria)
print(f"\n[INFO] Desde modulo TOLLS (cargado):")
print(f"   Total de peajes: {len(TOLLS)}")
print(f"   Activos: {sum(1 for t in TOLLS if t.get('status') == 'ACTIVE')}")
print(f"   Suspendidos: {sum(1 for t in TOLLS if t.get('status') == 'SUSPENDED')}")
print(f"   Removidos: {sum(1 for t in TOLLS if t.get('status') == 'REMOVED')}")
print(f"   Con coordenadas: {sum(1 for t in TOLLS if 'latitude' in t and 'longitude' in t)}")
print(f"   Con tarifa > 0: {sum(1 for t in TOLLS if t.get('fare_cop', 0) > 0)}")

# Estadísticas desde archivo JSON
try:
    with open('data/tolls_data.json', 'r', encoding='utf-8') as f:
        json_tolls = json.load(f)
    
    print(f"\n[INFO] Desde archivo tolls_data.json:")
    print(f"   Total de peajes: {len(json_tolls)}")
    print(f"   Activos: {sum(1 for t in json_tolls if t.get('status') == 'ACTIVE')}")
    print(f"   Con coordenadas: {sum(1 for t in json_tolls if 'latitude' in t and 'longitude' in t)}")
    print(f"   Con tarifa > 0: {sum(1 for t in json_tolls if t.get('fare_cop', 0) > 0)}")
    
    # Departamentos únicos
    depts = set(t.get('department', 'N/A') for t in json_tolls)
    print(f"\n[INFO] Departamentos: {len(depts)}")
    print(f"   {', '.join(sorted(depts)[:10])}{'...' if len(depts) > 10 else ''}")
    
except Exception as e:
    print(f"\n[ERROR] Error leyendo JSON: {e}")

print("\n" + "=" * 60)

