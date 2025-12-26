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
    from app.routes import all_blueprints
    for bp in all_blueprints:
        app.register_blueprint(bp, url_prefix='/api')
    
    # Route de santé
    @app.route('/health')
    def health():
        return {'status': 'ok', 'message': 'Bookly API is running'}, 200
    
    return app