"""
Vercel serverless function wrapper for Flask app
Vercel detecta automáticamente Flask cuando exportamos 'app'
"""
import sys
import os

# Agregar el directorio raíz al path para imports
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Configurar DB_FILE para Vercel antes de importar app
# En Vercel, /tmp es el único directorio escribible
if os.path.exists('/tmp'):
    os.environ['DB_FILE'] = os.path.join('/tmp', 'biatrack.db')

# Importar la aplicación Flask
# Esto inicializará la app y cargará todos los módulos
from app import app

# Inicializar la base de datos si estamos en Vercel
if os.path.exists('/tmp'):
    try:
        from app import init_db
        init_db()
    except Exception as e:
        # Si falla, continuar de todas formas
        print(f"Warning: Could not initialize DB: {e}")

# Exportar la aplicación Flask
# Vercel detectará automáticamente Flask y lo ejecutará como WSGI
__all__ = ['app']
