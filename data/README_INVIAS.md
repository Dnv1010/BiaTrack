# Integración de Datos de Peajes de INVIAS

Este directorio contiene scripts para descargar y procesar datos oficiales de peajes del Instituto Nacional de Vías (INVIAS) de Colombia.

## Archivos

- `download_invias_tolls.py`: Descarga datos oficiales de peajes desde la API de ArcGIS de INVIAS
- `parse_invias_tolls.py`: Convierte los datos GeoJSON de INVIAS al formato usado por BiaTrack
- `peajes_colombia.geojson`: Archivo GeoJSON descargado con todos los peajes oficiales
- `tolls_data_invias.json`: Peajes de INVIAS parseados en formato BiaTrack
- `tolls_data.json`: Archivo fusionado con peajes existentes y peajes de INVIAS

## Uso

### Descargar datos de INVIAS

```bash
python data/download_invias_tolls.py
```

Esto descargará todos los peajes oficiales desde la API de INVIAS y los guardará en `peajes_colombia.geojson`.

### Parsear y fusionar datos

```bash
python data/parse_invias_tolls.py
```

Esto:
1. Parsea el GeoJSON de INVIAS
2. Lo convierte al formato de BiaTrack
3. Lo fusiona con los peajes existentes (que tienen tarifas)
4. Guarda el resultado en `tolls_data.json`

## Estadísticas Actuales

- **Total de peajes**: 256
- **Con coordenadas**: 180
- **Con tarifa**: 184

## Notas

- Los peajes de INVIAS no incluyen tarifas, por lo que se mantienen en 0 COP
- Las coordenadas provienen directamente de la API oficial de INVIAS
- Los peajes existentes con tarifas se mantienen y se complementan con coordenadas de INVIAS cuando están disponibles

