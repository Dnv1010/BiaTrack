# Seguridad - Manejo de Claves API

## ⚠️ Importante: Clave API de Google Maps Expuesta

Se detectó que una clave de API de Google Maps fue expuesta en el archivo `config.json`. 

### Acciones Tomadas

1. ✅ **`config.json` agregado a `.gitignore`**: El archivo ya no será rastreado por git
2. ✅ **Clave removida**: La clave real fue reemplazada por un placeholder
3. ✅ **Archivo ejemplo creado**: `config.json.example` muestra el formato esperado

### Próximos Pasos Requeridos

**Si esta clave fue comprometida:**

1. **Revocar la clave inmediatamente** en Google Cloud Console:
   - Ve a [Google Cloud Console](https://console.cloud.google.com/)
   - Navega a "APIs & Services" > "Credentials"
   - Encuentra la clave `AIzaSyCZcOwTuEr4hshE5DZRD0s6zt5UiiuYyaU`
   - Revócala o elimínala

2. **Crear una nueva clave** con restricciones apropiadas:
   - Restringe por IP si es posible
   - Restringe por dominio/referrer HTTP
   - Limita las APIs que puede usar

3. **Remover del historial de git** (si es necesario):
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch config.json" \
     --prune-empty --tag-name-filter cat -- --all
   ```

### Uso Seguro de Claves API

**NUNCA** cometas archivos con claves reales. En su lugar:

1. Usa variables de entorno:
   ```python
   import os
   api_key = os.getenv('GOOGLE_MAPS_API_KEY')
   ```

2. O usa un archivo `.env` (ya está en `.gitignore`):
   ```bash
   GOOGLE_MAPS_API_KEY=tu_clave_aqui
   ```

3. Copia `config.json.example` a `config.json` y agrega tu clave localmente (no lo commitees)

### Nota

Actualmente, el código de la aplicación **NO utiliza** la clave de Google Maps API (se usa OSRM para routing). El archivo `config.json` parece ser un residuo de una implementación anterior.

