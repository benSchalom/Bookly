from flask import Flask #flask
from flask_sqlalchemy import SQLAlchemy #sql
from flask_jwt_extended import JWTManager #jwt
from flask_cors import CORS #cross origin resource sharing
from flask_migrate import Migrate #migration
from config import config #mes config


# extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_name='development'):
    app = Flask(__name__)

    #chargement des configurations
    app.config.from_object(config[config_name])
    app.config["JSON_AS_ASCII"] = False
    app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

    #Initialisation des extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})

    # Routes
    from app.routes import auth_bp
    app.register_blueprint(auth_bp)
    from app.routes.services import services_bp
    app.register_blueprint(services_bp)
    from app.routes.availabilities import availabilities_bp
    app.register_blueprint(availabilities_bp)
    from app.routes.time_blocks import time_blocks_bp
    app.register_blueprint(time_blocks_bp)
    from app.routes.appointments import appointments_bp
    app.register_blueprint(appointments_bp)
    
    # Route de santé
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'Bookly API is running'}, 200
    
    return app