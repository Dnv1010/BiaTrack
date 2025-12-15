# BiaTrack - Calculadora de Traslados

Aplicación web Python (Flask) para calcular costos de traslados en Colombia con cálculo automático de rutas, detección de peajes y visualización en mapa interactivo.

## Características

- ✅ **Cálculo automático de rutas** usando OSRM (Open Source Routing Machine)
- ✅ **Detección automática de peajes** basada en la geometría de la ruta
- ✅ **Geocodificación de ciudades** usando Nominatim (OpenStreetMap)
- ✅ **Visualización interactiva** de rutas y peajes en mapa Leaflet
- ✅ **Cálculo de costos** de combustible y peajes
- ✅ **Soporte para ida y regreso** con cálculo de rutas inversas
- ✅ **Dashboard de cálculos guardados**
- ✅ **Exportación a CSV**
- ✅ **Persistencia en SQLite**
- ✅ **Base de datos de peajes completa** con más de 280 peajes activos en Colombia

## Requisitos

- Python 3.8 o superior
- Conexión a Internet (para OSRM y Nominatim)

## Instalación

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

2. (Opcional) Configura variables de entorno:
```bash
# Windows PowerShell
$env:FLASK_ENV="development"

# Linux/Mac
export FLASK_ENV=development
```

## Uso

1. Ejecuta la aplicación:
```bash
python app.py
```

2. Abre tu navegador en: http://localhost:5000

3. Completa el formulario:
   - Selecciona contratista y base (se auto-completa el origen)
   - Ingresa el destino (con autocompletado de ciudades)
   - Ingresa precio por litro de combustible
   - Marca "Ida y Regreso" si aplica
   - Haz clic en "Calcular Ruta"
   - Revisa los resultados en el mapa y las tarjetas de información
   - Guarda el cálculo si deseas

## Estructura del Proyecto

```
BiaTrack/
├── app.py                      # Aplicación Flask principal
├── requirements.txt            # Dependencias Python
├── biatrack.db                # Base de datos SQLite (se crea automáticamente)
├── config.json.example        # Plantilla de configuración
├── SECURITY.md                # Documentación de seguridad
├── data/
│   ├── contractors.py         # Datos de contratistas y bases
│   ├── tolls.py              # Carga de datos de peajes
│   ├── tolls_data.json       # Base de datos de peajes (280+ peajes)
│   ├── tolls_parser.py       # Parser de datos de peajes
│   ├── parse_invias_tolls.py # Parser de datos INVIAS
│   └── parse_peajes_geojson.py # Parser de GeoJSON de peajes
├── services/
│   ├── geocoding.py          # Servicio de geocodificación
│   ├── routing.py            # Servicio de cálculo de rutas (OSRM)
│   └── toll_calculator.py   # Calculadora de peajes en rutas
└── templates/
    └── index.html            # Template HTML principal con Leaflet
```

## API Endpoints

- `GET /` - Página principal
- `GET /api/buscar_ciudad?q=<query>` - Autocompletado de ciudades
- `GET /api/calcular_ruta_supply` - Calcular ruta con distancia, tiempo, peajes y costos
- `POST /api/trip` - Crear nuevo cálculo
- `DELETE /api/trip/<id>` - Eliminar cálculo
- `GET /api/trips/export` - Exportar todos los cálculos a CSV
- `GET /api/contractors` - Obtener lista de contratistas
- `GET /api/tolls` - Obtener lista de peajes

## Base de Datos de Peajes

La aplicación incluye una base de datos completa de peajes en Colombia:
- **280+ peajes activos** con información detallada
- **239 peajes con coordenadas** para detección automática
- Datos de tarifas, operadores y departamentos
- Integración con datos oficiales de INVIAS

Los peajes se cargan automáticamente desde `data/tolls_data.json` al iniciar la aplicación.

## Notas Técnicas

- **Routing**: Usa OSRM (servidor público) para cálculo de rutas sin necesidad de API keys
- **Geocoding**: Usa Nominatim (OpenStreetMap) para geocodificación gratuita
- **Detección de peajes**: Algoritmo basado en distancia perpendicular a la ruta con validación de dirección
- **Persistencia**: SQLite para almacenamiento local de cálculos
- **Visualización**: Leaflet.js para mapas interactivos

## Seguridad

- ⚠️ **IMPORTANTE**: Nunca commitees archivos `config.json` con claves API reales
- Usa `config.json.example` como plantilla
- Revisa `SECURITY.md` para más información sobre manejo seguro de credenciales

## Licencia

Este proyecto es de uso interno.
