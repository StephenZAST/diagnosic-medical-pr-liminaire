"""
Service NLP pour extraction et analyse des symptômes
Utilise SpaCy pour le traitement du langage naturel
"""
try:
    import spacy
except Exception:  # pragma: no cover - optional dependency
    spacy = None
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class NLPService:
    """Service pour traitement langage naturel des symptômes"""
    
    def __init__(self, model_name='fr_core_news_sm'):
        """
        Initialise le service NLP
        
        Args:
            model_name (str): Nom du modèle SpaCy à charger
        """
        self.nlp = None
        if spacy is not None:
            try:
                self.nlp = spacy.load(model_name)
                logger.info(f'Modèle NLP {model_name} chargé avec succès')
            except OSError:
                logger.warning(f'Modèle {model_name} non trouvé. Utilisation du moteur de secours NLP.')
        else:
            logger.warning('SpaCy non disponible. Utilisation du moteur de secours NLP.')
    
    def extract_symptoms(self, text: str) -> List[str]:
        """
        Extrait les symptômes d'un texte en langage naturel
        
        Args:
            text (str): Texte contenant les symptômes
            
        Returns:
            List[str]: Liste des symptômes identifiés
        """
        if self.nlp is None:
            keyword_map = [
                'fièvre', 'toux', 'mal à la tête', 'migraine', 'nausée', 'fatigue',
                'douleur', 'rhume', 'allergie', 'vomissement', 'diarrhée', 'gorge',
                'vertiges', 'congestion', 'éternuement'
            ]
            text_lower = text.lower()
            symptoms = [kw for kw in keyword_map if kw in text_lower]
            if not symptoms:
                symptoms = ['symptômes généraux']
            return symptoms

        doc = self.nlp(text.lower())
        
        # Entités nommées potentielles (symptoms)
        symptoms = []
        for token in doc:
            if token.pos_ in ['NOUN', 'ADJ']:
                symptoms.append(token.text)
        
        # Nettoyage doublets
        symptoms = list(set(symptoms))
        
        logger.debug(f'Symptômes extraits: {symptoms}')
        return symptoms
    
    def normalize_text(self, text: str) -> str:
        """
        Normalise le texte d'entrée
        
        Args:
            text (str): Texte à normaliser
            
        Returns:
            str: Texte normalisé
        """
        if self.nlp is None:
            return text.lower().strip()

        doc = self.nlp(text.lower().strip())
        
        # Lemmatisation
        normalized = ' '.join([token.lemma_ for token in doc])
        
        return normalized
    
    def analyze_symptoms(self, text: str) -> Dict:
        """
        Analyse complète des symptômes
        
        Args:
            text (str): Description des symptômes
            
        Returns:
            Dict: Analyse détaillée
        """
        if self.nlp is None:
            analysis = {
                'original_text': text,
                'normalized_text': self.normalize_text(text),
                'symptoms': self.extract_symptoms(text),
                'sentiment': self._analyze_severity(text),
                'entities': []
            }
            return analysis

        doc = self.nlp(text.lower())
        
        analysis = {
            'original_text': text,
            'normalized_text': self.normalize_text(text),
            'symptoms': self.extract_symptoms(text),
            'sentiment': self._analyze_severity(doc),
            'entities': self._extract_entities(doc)
        }
        
        return analysis
    
    def _analyze_severity(self, doc_or_text) -> str:
        """
        Analyse la sévérité basée sur les mots-clés
        
        Args:
            doc_or_text: Document SpaCy ou texte brut
            
        Returns:
            str: Niveau de sévérité (léger, modéré, grave)
        """
        severity_words = {
            'grave': ['grave', 'sévère', 'intense', 'extrême', 'critique'],
            'modéré': ['modéré', 'notable', 'important'],
            'léger': ['léger', 'bénin', 'faible', 'doux']
        }
        
        text = doc_or_text.text.lower() if hasattr(doc_or_text, 'text') else str(doc_or_text).lower()
        
        for level, words in severity_words.items():
            if any(word in text for word in words):
                return level
        
        return 'modéré'  # Default
    
    def _extract_entities(self, doc) -> List[Dict]:
        """
        Extrait les entités nommées
        
        Args:
            doc: Document SpaCy
            
        Returns:
            List[Dict]: Entités identifiées
        """
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_
            })
        
        return entities
    
    def similarity_score(self, text1: str, text2: str) -> float:
        """
        Calcule la similarité entre deux textes
        
        Args:
            text1 (str): Premier texte
            text2 (str): Deuxième texte
            
        Returns:
            float: Score de similarité (0-1)
        """
        if self.nlp is None:
            return 0.0

        doc1 = self.nlp(text1.lower())
        doc2 = self.nlp(text2.lower())
        
        return float(doc1.similarity(doc2))


# Instance globale (singleton)
_nlp_service = None

def get_nlp_service(model_name='fr_core_news_sm'):
    """
    Récupère ou crée l'instance du service NLP
    
    Args:
        model_name (str): Modèle à utiliser
        
    Returns:
        NLPService: Instance du service
    """
    global _nlp_service
    if _nlp_service is None:
        _nlp_service = NLPService(model_name)
    return _nlp_service
