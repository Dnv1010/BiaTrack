# Integración de Peajes desde GeoJSON Oficial

Este directorio contiene scripts para procesar el archivo GeoJSON oficial de peajes de INVIAS.

## Archivo Base

- `Peajes.geojson`: Archivo GeoJSON oficial con todos los peajes de Colombia desde INVIAS

## Scripts

- `parse_peajes_geojson.py`: Parsea el GeoJSON oficial y lo convierte al formato de BiaTrack

## Uso

### Procesar el GeoJSON oficial

```bash
python data/parse_peajes_geojson.py
```

Esto:
1. Parsea el archivo `Peajes.geojson`
2. Extrae coordenadas, nombres, departamentos, operadores y tarifas
3. Lo fusiona con los peajes existentes (manteniendo tarifas actualizadas)
4. Guarda el resultado en `tolls_data.json`

## Estructura del GeoJSON

El archivo GeoJSON contiene features con:
- `properties.nombrepeaje`: Nombre del peaje
- `properties.latitud` / `properties.longitud`: Coordenadas (a veces duplicadas incorrectamente)
- `properties.categoriai`, `categoriaii`, etc.: Tarifas por categoría de vehículo
- `properties.territorial`: Código del departamento
- `properties.responsable`: Operador del peaje
- `geometry.coordinates`: Coordenadas en formato [longitude, latitude]

## Estadísticas Actuales

- **Total de peajes**: 281
- **Con coordenadas**: 239
- **Con tarifa**: 206
- **Activos**: 275

## Notas

- Las coordenadas se priorizan desde `geometry.coordinates` (más confiables)
- Si un peaje del GeoJSON tiene el mismo nombre que uno existente, se fusionan los datos
- Los peajes marcados como "NO OPERATIVO" se marcan como SUSPENDED
- La tarifa se toma de `categoriai` (Categoría I - vehículos ligeros)

