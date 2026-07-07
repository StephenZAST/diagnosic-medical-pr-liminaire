"""
Application Flask principale - Chatbot Diagnostic Médical
Initialisation et configuration de l'application
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import get_config
import logging
import os

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(env=None):
    """
    Fabrique d'application Flask
    
    Args:
        env (str): Environnement ('development', 'testing', 'production')
    
    Returns:
        Flask: Application Flask configurée
    """
    app = Flask(__name__)
    
    # Configuration
    config = get_config(env)
    app.config.from_object(config)
    
    # Extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    jwt = JWTManager(app)
    
    # Création répertoires logs si nécessaire
    os.makedirs('logs', exist_ok=True)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        """Vérifier que l'application est accessible"""
        return jsonify({
            'status': 'healthy',
            'environment': config.__name__
        }), 200
    
    # Enregistrement blueprints (à faire)
    # from routes.auth import auth_bp
    # from routes.chat import chat_bp
    # from routes.user import user_bp
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # app.register_blueprint(chat_bp, url_prefix='/api/chat')
    # app.register_blueprint(user_bp, url_prefix='/api/user')
    
    # Handlers erreurs
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal error: {error}')
        return jsonify({'error': 'Internal server error'}), 500
    
    # Enregistrement blueprints
    from routes.auth import auth_bp
    from routes.chat import chat_bp
    from routes.diagnostic import diagnostic_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(diagnostic_bp, url_prefix='/api/diagnostic')
    
    logger.info(f'Application créée en mode {config.__name__}')
    logger.info('Routes enregistrées: /api/auth, /api/chat, /api/diagnostic')
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
