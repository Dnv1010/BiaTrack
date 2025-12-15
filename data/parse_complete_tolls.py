"""
Script para parsear los datos completos de peajes proporcionados por el usuario
"""

import re
from typing import List, Dict

def parse_complete_tolls(file_path: str) -> List[Dict]:
    """
    Parsea el archivo de peajes completo con formato:
    DEPARTAMENTO
    Nombre | Operador | $Tarifa | Estado
    """
    tolls = []
    current_department = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detectar departamento (líneas en mayúsculas sin |)
        if line.isupper() and '|' not in line and len(line) > 3:
            current_department = line
            continue
        
        # Detectar peaje (líneas con |)
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            
            if len(parts) >= 3:
                name = parts[0].strip()
                operator = parts[1].strip() if len(parts) > 1 else ''
                
                # Extraer tarifa
                fare_str = parts[2] if len(parts) > 2 else parts[1] if len(parts) == 2 else '0'
                fare_match = re.search(r'[\d.]+', fare_str.replace(',', '').replace('$', '').strip())
                fare_cop = int(float(fare_match.group())) if fare_match else 0
                
                # Estado
                status = 'ACTIVE'
                if len(parts) >= 4:
                    status_str = parts[3].upper()
                    if 'REMOVED' in status_str or 'DESMONTADO' in status_str:
                        status = 'REMOVED'
                        fare_cop = 0
                    elif 'SUSPENDED' in status_str or 'SUSPENDIDO' in status_str or 'SIN COBRO' in status_str:
                        status = 'SUSPENDED'
                        if fare_cop == 0:
                            pass  # Ya es 0
                    elif 'ACTIVE' in status_str:
                        status = 'ACTIVE'
                elif fare_cop == 0:
                    status = 'SUSPENDED'
                
                # Limpiar nombre (remover asteriscos y notas)
                name = re.sub(r'\s*\([^)]*\)\s*', '', name)  # Remover paréntesis
                name = name.replace('*', '').strip()
                
                # Ignorar si dice "ya no existe" o similar
                if 'ya no existe' in name.lower() or 'desmontado' in name.lower():
                    status = 'REMOVED'
                    fare_cop = 0
                
                toll = {
                    'name': name,
                    'department': current_department or 'COLOMBIA',
                    'operator': operator,
                    'fare_cop': fare_cop,
                    'status': status
                }
                
                tolls.append(toll)
    
    return tolls

if __name__ == '__main__':
    import json
    import os
    
    # Parsear peajes
    tolls = parse_complete_tolls(os.path.join('data', 'tolls_data_complete.txt'))
    
    # Normalizar y agregar IDs
    normalized_tolls = []
    for i, toll in enumerate(tolls):
        toll_id = f"toll-{i+1}-{toll['name'].lower().replace(' ', '-').replace('(', '').replace(')', '')[:30]}"
        normalized_tolls.append({
            'id': toll_id,
            'name': toll['name'],
            'department': toll['department'],
            'operator': toll['operator'] or None,
            'fare_cop': toll['fare_cop'],
            'status': toll['status']
        })
    
    # Guardar en JSON
    output_path = os.path.join('data', 'tolls_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(normalized_tolls, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Se cargaron {len(normalized_tolls)} peajes")
    print(f"[OK] Archivo guardado en: {output_path}")
    
    # Estadísticas
    active = sum(1 for t in normalized_tolls if t['status'] == 'ACTIVE')
    removed = sum(1 for t in normalized_tolls if t['status'] == 'REMOVED')
    suspended = sum(1 for t in normalized_tolls if t['status'] == 'SUSPENDED')
    
    print(f"\nEstadisticas:")
    print(f"   - Activos: {active}")
    print(f"   - Removidos: {removed}")
    print(f"   - Suspendidos: {suspended}")

