"""
Routes pour le diagnostic
"""
from flask import Blueprint, request, jsonify
from services.ml_service import get_ml_service
import json
import logging

logger = logging.getLogger(__name__)

diagnostic_bp = Blueprint('diagnostic', __name__)

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


@diagnostic_bp.route('/predict', methods=['POST'])
def predict_disease():
    """Prédit les maladies possibles"""
    try:
        data = _parse_json_payload()
        symptoms = data.get('symptoms', [])
        
        if not symptoms:
            return jsonify({'error': 'Aucun symptôme fourni'}), 400
        
        prediction = ml_service.predict_disease(symptoms)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        }), 200
    
    except Exception as e:
        logger.error(f'Erreur predict_disease: {str(e)}')
        return jsonify({'error': 'Erreur serveur'}), 500


@diagnostic_bp.route('/risk-level', methods=['POST'])
def get_risk_level():
    """Calcule le niveau de risque"""
    try:
        data = _parse_json_payload()
        disease = data.get('disease', '')
        symptoms = data.get('symptoms', [])
        
        if not disease:
            return jsonify({'error': 'Maladie non spécifiée'}), 400
        
        risk_score = ml_service.calculate_risk_score(symptoms, disease)
        
        # Déterminer le niveau
        if risk_score > 0.7:
            risk_level = 'ÉLEVÉE'
        elif risk_score > 0.4:
            risk_level = 'MODÉRÉE'
        else:
            risk_level = 'BASSE'
        
        return jsonify({
            'success': True,
            'risk_score': risk_score,
            'risk_level': risk_level
        }), 200
    
    except Exception as e:
        logger.error(f'Erreur get_risk_level: {str(e)}')
        return jsonify({'error': 'Erreur serveur'}), 500


@diagnostic_bp.route('/recommendations', methods=['POST'])
def get_recommendations():
    """Récupère les recommandations médicales"""
    try:
        data = _parse_json_payload()
        disease = data.get('disease', '')
        risk_score = data.get('risk_score', data.get('riskScore', 0.5))
        
        if not disease:
            return jsonify({'error': 'Maladie non spécifiée'}), 400
        
        recommendations = ml_service.generate_recommendations(disease, risk_score)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        }), 200
    
    except Exception as e:
        logger.error(f'Erreur get_recommendations: {str(e)}')
        return jsonify({'error': 'Erreur serveur'}), 500
