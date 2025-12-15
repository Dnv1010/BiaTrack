"""Script de prueba para verificar la carga de peajes"""

from data.tolls import TOLLS

print(f'Total peajes cargados: {len(TOLLS)}')
print(f'Con coordenadas: {sum(1 for t in TOLLS if "latitude" in t)}')
print(f'Con tarifa: {sum(1 for t in TOLLS if t.get("fare_cop", 0) > 0)}')

# Mostrar algunos ejemplos
print("\nEjemplos de peajes con coordenadas:")
count = 0
for toll in TOLLS:
    if 'latitude' in toll and count < 5:
        print(f"  - {toll.get('name')}: ({toll.get('latitude')}, {toll.get('longitude')})")
        count += 1

