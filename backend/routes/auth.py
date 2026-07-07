"""
Routes d'authentification
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

# Mock users pour développement
MOCK_USERS = {
    'user@example.com': 'password123'
}

@auth_bp.route('/register', methods=['POST'])
def register():
    """Enregistrer un nouvel utilisateur"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email et mot de passe requis'}), 400
        
        if email in MOCK_USERS:
            return jsonify({'error': 'Utilisateur déjà existant'}), 409
        
        # En production: hasher le mot de passe avec bcrypt
        MOCK_USERS[email] = password
        
        return jsonify({
            'message': 'Utilisateur créé avec succès',
            'email': email
        }), 201
    
    except Exception as e:
        logger.error(f'Erreur registration: {str(e)}')
        return jsonify({'error': 'Erreur serveur'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Connexion utilisateur"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Identifiants manquants'}), 400
        
        # Vérifier les credentials
        if email not in MOCK_USERS or MOCK_USERS[email] != password:
            return jsonify({'error': 'Identifiants invalides'}), 401
        
        # Créer JWT token
        access_token = create_access_token(identity=email)
        
        return jsonify({
            'access_token': access_token,
            'email': email,
            'message': 'Connexion réussie'
        }), 200
    
    except Exception as e:
        logger.error(f'Erreur login: {str(e)}')
        return jsonify({'error': 'Erreur serveur'}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Déconnexion utilisateur"""
    return jsonify({'message': 'Déconnecté avec succès'}), 200
