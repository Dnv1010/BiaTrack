# Despliegue en Vercel

## Configuración para Vercel

Este proyecto está configurado para desplegarse en Vercel usando Flask como aplicación serverless.

### Archivos de Configuración

- **`vercel.json`**: Configuración de rutas y builds para Vercel
- **`api/index.py`**: Wrapper serverless para Flask
- **`.vercelignore`**: Archivos que no deben desplegarse

### Pasos para Desplegar

1. **Instalar Vercel CLI** (si no lo tienes):
   ```bash
   npm i -g vercel
   ```

2. **Iniciar sesión en Vercel**:
   ```bash
   vercel login
   ```

3. **Desplegar el proyecto**:
   ```bash
   vercel
   ```

4. **Para producción**:
   ```bash
   vercel --prod
   ```

### Variables de Entorno

Si necesitas variables de entorno, configúralas en Vercel Dashboard:
- Ve a tu proyecto en Vercel
- Settings > Environment Variables
- Agrega las variables necesarias

### Notas Importantes

- **Base de datos SQLite**: En Vercel, SQLite funciona en modo read-only. Si necesitas escritura, considera usar una base de datos externa.
- **Archivos estáticos**: Los templates y archivos estáticos se sirven desde el directorio `templates/` y `static/` respectivamente.
- **Rutas**: Todas las rutas se redirigen a `/api/index.py` que ejecuta la aplicación Flask.

### Estructura para Vercel

```
BiaTrack/
├── api/
│   └── index.py          # Wrapper serverless
├── app.py                # Aplicación Flask principal
├── vercel.json           # Configuración Vercel
├── .vercelignore         # Archivos a ignorar
└── requirements.txt      # Dependencias Python
```

### Solución de Problemas

Si ves la versión de Next.js (puerto 3000) en lugar de Flask:

1. Verifica que `vercel.json` existe y está configurado correctamente
2. Verifica que `api/index.py` existe y exporta la app Flask
3. Elimina el build anterior: `vercel --force`
4. Redespliega: `vercel --prod`

### Comandos Útiles

```bash
# Ver logs en tiempo real
vercel logs

# Ver información del proyecto
vercel inspect

# Eliminar despliegue
vercel remove
```

