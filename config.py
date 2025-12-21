import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class Config:
    #configuratrion de base
    SECRET_KEY = os.getenv('SECRET_KEY', 'b6fe223951282133911c01b3bbc1c2ebbdfa300cd552c2464a022dd8ad617403')
    JSON_AS_ASCII = False
    
    # Base de donnee
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'bookly')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

    #chaine de connexion
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #configuration JWT (token pour chaque requete, anti bot)
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))

    # CORS restriction sur l'appel de mon API
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:8080').split(',')

class DevelopmentConfig(Config):
    #Configuration en mode developement
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    #Configuration production
    DEBUG = False
    TESTING = False 

class TestingConfig(Config):
    #Configuration tests
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI', 'sqlite:///:memory:')

#Dictionnaire de configuration
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}