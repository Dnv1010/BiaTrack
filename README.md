# BiaTrack - Calculadora de Traslados

Aplicación web Python (Flask) para calcular costos de traslados en Colombia con obtención automática de distancia y tiempo desde Google Maps API.

## Características

- ✅ Obtención automática de distancia y tiempo desde Google Maps API
- ✅ Cálculo de costos de combustible (Gasolina o ACPM)
- ✅ Selección manual de peajes
- ✅ Cálculo de tiempo en hora pico (3.5x)
- ✅ Dashboard de cálculos guardados
- ✅ Exportación a CSV
- ✅ Persistencia en SQLite

## Requisitos

- Python 3.8 o superior
- Google Maps API Key (Distance Matrix API)

## Instalación

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

2. Configura tu API Key de Google Maps:
```bash
# Windows PowerShell
$env:GOOGLE_MAPS_API_KEY="tu-api-key-aqui"

# Linux/Mac
export GOOGLE_MAPS_API_KEY="tu-api-key-aqui"
```

## Uso

1. Ejecuta la aplicación:
```bash
python app.py
```

2. Abre tu navegador en: http://localhost:5000

3. Completa el formulario:
   - Selecciona contratista y base
   - Ingresa el destino (la distancia y tiempo se obtendrán automáticamente)
   - Ingresa precio por galón
   - Ajusta rendimiento si es necesario (por defecto 30 km/gal)
   - Selecciona peajes si aplican
   - Guarda el cálculo

## Estructura del Proyecto

```
BiaTrack/
├── app.py                 # Aplicación Flask principal
├── requirements.txt        # Dependencias Python
├── biatrack.db           # Base de datos SQLite (se crea automáticamente)
├── data/
│   ├── contractors.py     # Datos de contratistas y bases
│   └── tolls.py          # Datos de peajes
└── templates/
    └── index.html        # Template HTML principal
```

## API Endpoints

- `GET /` - Página principal
- `POST /api/route` - Obtener distancia y tiempo desde Google Maps
- `POST /api/trip` - Crear nuevo cálculo
- `DELETE /api/trip/<id>` - Eliminar cálculo
- `GET /api/trips/export` - Exportar todos los cálculos a CSV

## Notas

- La aplicación requiere una API Key válida de Google Maps con Distance Matrix API habilitada
- Los datos se almacenan localmente en SQLite
- El cálculo funciona para vehículos Categoría I (livianos)
