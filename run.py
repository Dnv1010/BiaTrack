"""
Script para ejecutar BiaTrack
"""

import os
import sys

# Verificar que existe .env
if not os.path.exists('.env'):
    print("=" * 60)
    print("⚠️  ADVERTENCIA: No se encontró archivo .env")
    print("=" * 60)
    print("Creando archivo .env desde .env.example...")
    
    if os.path.exists('.env.example'):
        with open('.env.example', 'r') as f:
            content = f.read()
        with open('.env', 'w') as f:
            f.write(content)
        print("✓ Archivo .env creado. Por favor configura tu GOOGLE_MAPS_API_KEY")
    else:
        print("✗ No se encontró .env.example")
        print("\nCrea un archivo .env con:")
        print("GOOGLE_MAPS_API_KEY=tu_api_key_aqui")
        sys.exit(1)

# Ejecutar aplicación
if __name__ == '__main__':
    from app import app
    print("\n" + "=" * 60)
    print("🚀 BiaTrack - Calculadora de Traslados")
    print("=" * 60)
    print("📡 Servidor iniciando en http://localhost:5000")
    print("🌐 Abre tu navegador en: http://localhost:5000")
    print("⏹️  Presiona Ctrl+C para detener")
    print("=" * 60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)

