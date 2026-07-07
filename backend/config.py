"""
Configuration application Flask - Chatbot Diagnostic Médical
"""
import os
from datetime import timedelta

class Config:
    """Configuration de base"""
    
    # Flask Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # JWT Config
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # MongoDB Config
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/chatbot_medical'
    MONGO_DB_NAME = 'chatbot_medical'
    
    # CORS Config
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ]
    
    # NLP Config
    NLP_MODEL = 'fr_core_news_sm'  # Modèle SpaCy français
    
    # ML Config
    ML_MODEL_PATH = os.path.join(os.path.dirname(__file__), '../models/disease_predictor.pkl')
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/app.log'


class DevelopmentConfig(Config):
    """Configuration développement"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Configuration tests"""
    TESTING = True
    MONGODB_URI = 'mongodb://localhost:27017/chatbot_medical_test'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=10)


class ProductionConfig(Config):
    """Configuration production"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'
    # En production, s'assurer que tous les secrets sont définis
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    MONGODB_URI = os.environ.get('MONGODB_URI')


# Dictionnaire de configuration
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(env=None):
    """Récupère la configuration basée sur l'environnement"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
