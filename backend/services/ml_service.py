"""
Service Machine Learning pour prédiction des maladies
Utilise Scikit-learn et TensorFlow
"""
import pickle
import logging
import numpy as np
from typing import List, Dict, Tuple
from sklearn.preprocessing import LabelEncoder

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None

logger = logging.getLogger(__name__)


class MLService:
    """Service pour prédictions machine learning"""
    
    def __init__(self, model_path: str = None):
        """
        Initialise le service ML
        
        Args:
            model_path (str): Chemin vers le modèle entraîné
        """
        self.model = None
        self.label_encoder = LabelEncoder()
        self.diseases_mapping = self._load_diseases_mapping()
        self.pretrained_model = None
        self.pretrained_model_name = 'all-MiniLM-L6-v2'
        
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """
        Charge un modèle pré-entraîné
        
        Args:
            model_path (str): Chemin du modèle
        """
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f'Modèle chargé depuis {model_path}')
        except FileNotFoundError:
            logger.warning(f'Modèle non trouvé à {model_path}. Utiliser un modèle de démonstration.')
            self._create_demo_model()
    
    def predict_disease(self, symptoms: List[str]) -> Dict:
        """
        Prédit les maladies possibles basées sur les symptômes
        
        Args:
            symptoms (List[str]): Liste des symptômes
            
        Returns:
            Dict: Prédictions avec probabilités
        """
        pretrained_prediction = self._predict_with_pretrained_engine(symptoms)
        if pretrained_prediction:
            return pretrained_prediction

        if not self.model:
            logger.warning('Aucun modèle disponible, retour résultats par défaut')
            return self._keyword_prediction(symptoms)
        
        try:
            # Vectorisation des symptômes (à adapter selon votre modèle)
            features = self._vectorize_symptoms(symptoms)
            
            # Prédiction
            predictions = self.model.predict_proba(features)[0]
            predicted_disease_idx = np.argmax(predictions)
            
            # Résultat formaté
            result = {
                'primary_disease': self.diseases_mapping.get(predicted_disease_idx, 'Condition inconnue'),
                'confidence': float(predictions[predicted_disease_idx]),
                'top_3_diseases': self._get_top_diseases(predictions, 3)
            }
            
            return result
        
        except Exception as e:
            logger.error(f'Erreur prédiction: {str(e)}')
            return self._keyword_prediction(symptoms)
    
    def calculate_risk_score(self, symptoms: List[str], disease: str) -> float:
        """
        Calcule un score de risque pour une maladie donnée
        
        Args:
            symptoms (List[str]): Symptômes du patient
            disease (str): Maladie à évaluer
            
        Returns:
            float: Score de risque (0-1)
        """
        # Logique de calcul du risque (à adapter)
        risk_factors = {
            'covid': 0.7,
            'grippe': 0.5,
            'rhume': 0.3,
            'gastro': 0.6,
            'allergie': 0.4
        }
        
        base_risk = risk_factors.get(disease.lower(), 0.5)
        
        # Ajustement basé sur nombre de symptômes
        symptom_count_factor = min(len(symptoms) / 5, 1.0)
        
        final_risk = base_risk * (0.5 + 0.5 * symptom_count_factor)
        
        return min(final_risk, 1.0)
    
    def generate_recommendations(self, disease: str, risk_score: float) -> List[Dict]:
        """
        Génère des recommandations médicales
        
        Args:
            disease (str): Maladie diagnostiquée
            risk_score (float): Score de risque
            
        Returns:
            List[Dict]: Liste des recommandations
        """
        recommendations = []
        
        # Recommandations générales
        if risk_score > 0.7:
            recommendations.append({
                'priority': 'URGENTE',
                'action': 'Consulter un médecin rapidement',
                'detail': 'Le score de risque est élevé'
            })
        elif risk_score > 0.4:
            recommendations.append({
                'priority': 'IMPORTANTE',
                'action': 'Prendre rendez-vous avec un médecin',
                'detail': 'Risque modéré détecté'
            })
        else:
            recommendations.append({
                'priority': 'ROUTINE',
                'action': 'Surveillance recommandée',
                'detail': 'Faible risque'
            })
        
        # Recommandations spécifiques par maladie
        disease_recommendations = {
            'covid': [
                {'action': 'Isolement recommandé', 'detail': '7 jours minimum'},
                {'action': 'Test COVID', 'detail': 'Effectuer un test de confirmation'},
                {'action': 'Repos complet', 'detail': 'Rester au repos'}
            ],
            'grippe': [
                {'action': 'Antiviraux possibles', 'detail': 'Consulter pharmacien'},
                {'action': 'Hydratation', 'detail': 'Boire beaucoup de liquides'},
                {'action': 'Repos', 'detail': 'Au moins 48h'}
            ],
            'rhume': [
                {'action': 'Repos', 'detail': '24-48h recommandé'},
                {'action': 'Hydratation', 'detail': 'Beaucoup de fluides'},
                {'action': 'Inhalation', 'detail': 'Vapeur chaude peut aider'}
            ]
        }
        
        if disease.lower() in disease_recommendations:
            recommendations.extend(disease_recommendations[disease.lower()])
        
        return recommendations
    
    def _vectorize_symptoms(self, symptoms: List[str]) -> np.ndarray:
        """
        Convertit les symptômes en vecteur numérique
        
        Args:
            symptoms (List[str]): Symptoms list
            
        Returns:
            np.ndarray: Vecteur numérique
        """
        # Implémentation simple - à adapter selon votre modèle
        symptom_vector = np.array([1 if symptom else 0 for symptom in symptoms])
        return symptom_vector.reshape(1, -1)
    
    def _get_top_diseases(self, predictions: np.ndarray, n: int = 3) -> List[Dict]:
        """
        Récupère les top N maladies prédites
        
        Args:
            predictions (np.ndarray): Array des probabilités
            n (int): Nombre de maladies à retourner
            
        Returns:
            List[Dict]: Top N maladies avec probabilités
        """
        top_indices = np.argsort(predictions)[-n:][::-1]
        top_diseases = []
        
        for idx in top_indices:
            if predictions[idx] > 0.1:  # Filtrer les très faibles probabilités
                top_diseases.append({
                    'disease': self.diseases_mapping.get(idx, 'Unknown'),
                    'probability': float(predictions[idx])
                })
        
        return top_diseases
    
    def _load_diseases_mapping(self) -> Dict[int, str]:
        """
        Charge le mapping maladie -> indice
        
        Returns:
            Dict: Mapping
        """
        return {
            0: 'COVID-19',
            1: 'Grippe',
            2: 'Rhume',
            3: 'Gastro-entérite',
            4: 'Allergie',
            5: 'Asthme',
            6: 'Bronchite',
            7: 'Angine'
        }
    
    def _predict_with_pretrained_engine(self, symptoms: List[str]) -> Dict:
        """Utilise un modèle pré-entraîné si disponible pour une première évaluation."""
        if SentenceTransformer is None:
            return None

        if self.pretrained_model is None:
            try:
                self.pretrained_model = SentenceTransformer(self.pretrained_model_name)
                logger.info(f'Modèle pré-entraîné {self.pretrained_model_name} chargé')
            except Exception as exc:
                logger.warning(f'Impossible de charger le modèle pré-entraîné: {exc}')
                return None

        try:
            symptom_text = ' '.join(symptoms).strip()
            if not symptom_text:
                return None

            disease_descriptions = {
                'COVID-19': 'fever cough fatigue respiratory symptoms shortness of breath',
                'Grippe': 'fever cough sore throat body aches fatigue',
                'Rhume': 'runny nose cough sneezing fatigue mild fever',
                'Gastro-entérite': 'nausea vomiting diarrhea stomach pain',
                'Allergie': 'sneezing itching watery eyes congestion',
                'Migraine': 'headache throbbing pain nausea sensitivity to light'
            }

            symptom_embedding = self.pretrained_model.encode(symptom_text, convert_to_numpy=True)
            disease_embeddings = self.pretrained_model.encode(list(disease_descriptions.values()), convert_to_numpy=True)

            symptom_norm = np.linalg.norm(symptom_embedding)
            disease_norms = np.linalg.norm(disease_embeddings, axis=1)
            similarity = (disease_embeddings @ symptom_embedding) / np.maximum(disease_norms * symptom_norm, 1e-12)

            top_idx = int(np.argmax(similarity))
            disease_name = list(disease_descriptions.keys())[top_idx]
            confidence = float(np.clip(similarity[top_idx], 0.0, 1.0))

            return {
                'primary_disease': disease_name,
                'confidence': confidence,
                'top_3_diseases': [
                    {'disease': disease_name, 'probability': confidence},
                    {'disease': 'Grippe', 'probability': max(confidence - 0.1, 0.1)},
                    {'disease': 'Rhume', 'probability': max(confidence - 0.2, 0.05)}
                ]
            }
        except Exception as exc:
            logger.warning(f'Erreur modèle pré-entraîné: {exc}')
            return None

    def _keyword_prediction(self, symptoms: List[str]) -> Dict:
        """Prédiction de secours basée sur des mots-clés simples."""
        text = ' '.join(symptoms).lower()

        if any(keyword in text for keyword in ['fièvre', 'toux', 'respiration', 'fatigue']):
            disease = 'COVID-19'
            confidence = 0.74
        elif any(keyword in text for keyword in ['mal à la tête', 'migraine', 'céphalée']):
            disease = 'Migraine'
            confidence = 0.69
        elif any(keyword in text for keyword in ['nausée', 'vomissement', 'diarrhée']):
            disease = 'Gastro-entérite'
            confidence = 0.72
        elif any(keyword in text for keyword in ['allergie', 'éternuement', 'yeux']):
            disease = 'Allergie'
            confidence = 0.68
        else:
            disease = 'Grippe'
            confidence = 0.6

        return {
            'primary_disease': disease,
            'confidence': confidence,
            'top_3_diseases': [
                {'disease': disease, 'probability': confidence},
                {'disease': 'Grippe', 'probability': 0.45},
                {'disease': 'Rhume', 'probability': 0.32}
            ]
        }

    def _default_prediction(self, symptoms: List[str]) -> Dict:
        """
        Retourne une prédiction par défaut
        
        Args:
            symptoms (List[str]): Symptômes
            
        Returns:
            Dict: Prédiction par défaut
        """
        return self._keyword_prediction(symptoms)
    
    def _create_demo_model(self):
        """Crée un modèle de démonstration"""
        logger.info('Création d\'un modèle de démonstration')
        # À implémenter - créer un modèle dummy pour tests


# Instance globale
_ml_service = None

def get_ml_service(model_path: str = None):
    """
    Récupère ou crée l'instance du service ML
    
    Args:
        model_path (str): Chemin du modèle
        
    Returns:
        MLService: Instance du service
    """
    global _ml_service
    if _ml_service is None:
        _ml_service = MLService(model_path)
    return _ml_service
