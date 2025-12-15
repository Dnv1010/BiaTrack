# Corrección de vercel.json

## Problema
El archivo `vercel.json` tenía propiedades inválidas:
- `ignore` - No es una propiedad válida en vercel.json
- `buildCommand` - No necesario para funciones serverless
- `rewrites` - Redundante con `routes`

## Solución
Se simplificó `vercel.json` para usar solo propiedades válidas:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ]
}
```

## Archivos ignorados
Para ignorar archivos de Next.js y otros, usa `.vercelignore` (ya existe en el proyecto).

## Próximos pasos
1. Hacer commit del cambio
2. Hacer push al repositorio
3. Vercel debería detectar el cambio y redesplegar automáticamente

