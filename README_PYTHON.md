# BiaTrack - Versión Python

Calculadora de traslados automatizada para Colombia.

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar API Key de Google Maps:
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env y agregar tu API Key
GOOGLE_MAPS_API_KEY=tu_api_key_aqui
```

3. Ejecutar aplicación:
```bash
python app.py
```

4. Abrir en navegador:
```
http://localhost:5000
```

## Características

- ✅ Obtención automática de distancia y tiempo desde Google Maps
- ✅ Cálculo automático de costos de combustible y peajes
- ✅ Exportación a CSV
- ✅ Persistencia de datos en JSON
- ✅ Interfaz web moderna

## Estructura

```
BiaTrack/
├── app.py                 # Aplicación Flask principal
├── requirements.txt        # Dependencias Python
├── .env                   # Variables de entorno (crear desde .env.example)
├── data/
│   ├── contractors.py     # Datos de contratistas
│   └── tolls.py          # Datos de peajes
├── lib/
│   ├── maps_api.py       # Integración Google Maps
│   └── calculator.py     # Lógica de cálculo
├── templates/
│   └── index.html        # Interfaz web
└── data_storage/
    └── trips.json        # Viajes guardados (se crea automáticamente)
```

