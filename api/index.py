"""
Vercel serverless function wrapper for Flask app
"""
import sys
import os

# Agregar el directorio raíz al path para imports
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

# Para Vercel Python runtime, exportar la app Flask directamente
# Vercel detectará automáticamente la aplicación Flask y la ejecutará
handler = app
