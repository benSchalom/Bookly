import os
from app import create_app

# Créer l'application
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # Lancer le serveur
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('DEBUG', 'True') == 'True'
    
    print(f"Aster API on http://{host}:{port}")
    print(f"Environment: {config_name}")
    print(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)