# Solución de Problemas - Vercel Flask

## Error: FUNCTION_INVOCATION_FAILED (500)

### Cambios Realizados

1. **`api/index.py`** - Wrapper mejorado:
   - Configura `DB_FILE` para usar `/tmp` en Vercel (único directorio escribible)
   - Inicializa la base de datos antes de exportar la app
   - Maneja errores de inicialización gracefully

2. **`app.py`** - Actualizado:
   - `DB_FILE` ahora detecta automáticamente si está en Vercel (`/tmp` existe)
   - Usa variable de entorno `DB_FILE` si está disponible
   - Fallback a `biatrack.db` en local

### Verificación

El wrapper ahora:
- ✅ Configura el path correctamente
- ✅ Detecta Vercel y usa `/tmp` para la base de datos
- ✅ Inicializa la DB antes de exportar
- ✅ Exporta `app` que Vercel detecta automáticamente

### Próximos Pasos

1. Hacer commit y push:
   ```bash
   git add api/index.py app.py
   git commit -m "fix: Mejorar wrapper Vercel y configuración de DB"
   git push origin main
   ```

2. Vercel debería redesplegar automáticamente

3. Si aún hay errores, revisa los logs en Vercel Dashboard:
   - Ve a tu proyecto en Vercel
   - Click en "Functions" > "api/index.py"
   - Revisa los logs de error

### Notas sobre SQLite en Vercel

- **`/tmp`** es el único directorio escribible en funciones serverless
- Los archivos en `/tmp` son **efímeros** (se eliminan después de cada invocación)
- Para producción, considera usar una base de datos externa (PostgreSQL, MongoDB, etc.)

### Si el Error Persiste

1. Verifica que `requirements.txt` solo tenga dependencias válidas
2. Verifica que `vercel.json` tenga la sintaxis correcta
3. Revisa los logs completos en Vercel Dashboard
4. Considera agregar logging adicional en `api/index.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    from app import app
    logger.info("Flask app imported successfully")
except Exception as e:
    logger.error(f"Error importing Flask app: {e}", exc_info=True)
    raise
```

