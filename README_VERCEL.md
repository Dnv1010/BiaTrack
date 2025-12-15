# Despliegue en Vercel - BiaTrack Flask

## ✅ Configuración Completada

El proyecto está configurado para desplegarse en Vercel ejecutando Flask en lugar de Next.js.

### Archivos Creados/Modificados

1. **`vercel.json`** - Configuración principal de Vercel
   - Ignora el build de Next.js
   - Configura Flask como función serverless
   - Redirige todas las rutas a `/api/index.py`

2. **`api/index.py`** - Wrapper serverless para Flask
   - Exporta la aplicación Flask para Vercel
   - Maneja los imports correctamente

3. **`app.py`** - Actualizado
   - Configuración de templates y static folders explícita

4. **`.vercelignore`** - Archivos a ignorar en el despliegue
   - Excluye archivos de desarrollo y debug

5. **`VERCEL_DEPLOY.md`** - Documentación completa de despliegue

## 🚀 Pasos para Desplegar

### Opción 1: Desde Vercel Dashboard

1. Ve a [vercel.com](https://vercel.com)
2. Importa tu repositorio de GitHub
3. Vercel detectará automáticamente la configuración
4. Haz clic en "Deploy"

### Opción 2: Desde CLI

```bash
# Instalar Vercel CLI (si no lo tienes)
npm i -g vercel

# Iniciar sesión
vercel login

# Desplegar
vercel

# Para producción
vercel --prod
```

## 🔧 Configuración Actual

- **Framework**: Flask (Python)
- **Runtime**: Python 3.11 (Vercel detecta automáticamente)
- **Build**: Se omite el build de Next.js
- **Rutas**: Todas las rutas se manejan por Flask

## ⚠️ Notas Importantes

1. **Base de Datos SQLite**: 
   - En Vercel, SQLite funciona en modo read-only
   - Los archivos se escriben en `/tmp` que es efímero
   - Considera usar una base de datos externa para producción

2. **Archivos Estáticos**:
   - Los templates están en `templates/`
   - Los archivos estáticos deberían estar en `static/` (si los necesitas)

3. **Variables de Entorno**:
   - Configúralas en Vercel Dashboard > Settings > Environment Variables

## 🐛 Solución de Problemas

### Si ves Next.js en lugar de Flask:

1. Verifica que `vercel.json` existe y tiene la configuración correcta
2. Verifica que `api/index.py` existe y exporta `handler = app`
3. Elimina el despliegue anterior y redespliega:
   ```bash
   vercel --force
   vercel --prod
   ```

### Si hay errores de importación:

- Verifica que todos los módulos Python estén en el directorio correcto
- Asegúrate de que `requirements.txt` tiene todas las dependencias

## 📝 Verificación Post-Despliegue

Después de desplegar, verifica:

1. ✅ La aplicación carga en la URL de Vercel
2. ✅ Las rutas API funcionan (`/api/contractors`, `/api/tolls`, etc.)
3. ✅ El mapa Leaflet se carga correctamente
4. ✅ Los cálculos de rutas funcionan

## 🔗 URLs Esperadas

- **Producción**: `https://tu-proyecto.vercel.app`
- **Preview**: `https://tu-proyecto-git-branch.vercel.app`

La aplicación Flask debería estar disponible en todas estas URLs.

