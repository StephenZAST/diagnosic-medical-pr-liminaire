"""
Routes pour le chatbot et diagnostic
"""
from flask import Blueprint, request, jsonify
from services.nlp_service import get_nlp_service
from services.ml_service import get_ml_service
import json
import logging

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)

# Services
nlp_service = get_nlp_service()
ml_service = get_ml_service()

def _parse_json_payload():
    """Parse les données JSON avec une tolérance aux encodages non UTF-8."""
    try:
        payload = request.get_json(silent=True)
        if payload is not None:
            return payload
    except Exception:
        pass

    raw_data = request.get_data(cache=True)
    if not raw_data:
        return {}
    try:
        return json.loads(raw_data.decode('utf-8'))
    except Exception:
        try:
            return json.loads(raw_data.decode('utf-8', errors='ignore') or '{}')
        except Exception:
            return {}


@chat_bp.route('/send', methods=['POST'])
def send_message():
    """Reçoit et traite un message de l'utilisateur"""
    try:
        data = _parse_json_payload()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Message vide'}), 400
        
        # Analyser les symptômes avec NLP
        analysis = nlp_service.analyze_symptoms(message)
        symptoms = analysis['symptoms']
        
        # Prédire la maladie avec ML
        diagnosis = ml_service.predict_disease(symptoms)
        
        # Calculer le score de risque
        risk_score = ml_service.calculate_risk_score(
            symptoms,
            diagnosis['primary_disease']
        )
        
        # Générer recommandations
        recommendations = ml_service.generate_recommendations(
            diagnosis['primary_disease'],
            risk_score
        )
        
        return jsonify({
            'success': True,
            'analysis': {
                'symptoms': symptoms,
                'severity': analysis['sentiment']
            },
            'diagnosis': diagnosis,
            'risk_score': risk_score,
            'recommendations': recommendations
        }), 200
    
    except Exception as e:
        logger.error(f'Erreur send_message: {str(e)}')
        return jsonify({'error': 'Erreur serveur'}), 500


@chat_bp.route('/history', methods=['GET'])
def get_history():
    """Récupère l'historique des conversations (mock)"""
    return jsonify({
        'history': [
            {'message': 'J\'ai mal à la tête', 'response': 'Diagnostic: Migraine'},
            {'message': 'Fièvre et toux', 'response': 'Diagnostic: Grippe'}
        ]
    }), 200


@chat_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """Liste les sessions de chat"""
    return jsonify({
        'sessions': []
    }), 200
