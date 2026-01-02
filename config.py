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
    DB_NAME = os.getenv('DB_NAME', 'aster')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'mysql')

    #chaine de connexion
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #configuration JWT (token pour chaque requete, anti bot)
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'lhVT9qmWdEhZ0pH6pFLUiQ7rdhdyDmnACmV9iX27X9QiNPjTeNM65wt1wVlmxfWpeQSLKx0CSoma8UGDaQyVbw')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))

    # CORS restriction sur l'appel de mon API
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:8080').split(',')

    # configuration pou email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'mail.ser-vicescam.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 465))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'False') == 'True'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    #variable de calcul du prix de deplacement pour serviec a domicile
    TARIF_DEPLACEMENT_PAR_KM = 1.50 

class DevelopmentConfig(Config):
    #Configuration en mode developement
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    #Configuration production
    DEBUG = False
    TESTING = False 

#Dictionnaire de configuration
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


