/**
 * API Service - Gestion des appels à l'API backend
 */

const API_BASE_URL = 'http://127.0.0.1:5000/api';

/**
 * Classe pour gérer toutes les requêtes API
 */
class APIClient {
    /**
     * Envoyer les symptômes pour diagnostic
     * @param {string} symptoms - Description des symptômes
     * @returns {Promise} Réponse du serveur
     */
    static async sendSymptoms(symptoms) {
        try {
            const response = await fetch(`${API_BASE_URL}/chat/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: symptoms,
                    timestamp: new Date().toISOString()
                })
            });

            if (!response.ok) {
                throw new Error(`Erreur API: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Erreur lors de l\'envoi des symptômes:', error);
            return APIClient.getMockResponse(symptoms);
        }
    }

    /**
     * Obtenir le diagnostic préliminaire
     * @param {Array<string>} symptoms - Liste des symptômes
     * @returns {Promise} Diagnostic
     */
    static async getDiagnosis(symptoms) {
        try {
            const response = await fetch(`${API_BASE_URL}/diagnostic/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ symptoms })
            });

            if (!response.ok) {
                throw new Error(`Erreur API: ${response.status}`);
            }

            const data = await response.json();
            const prediction = data.prediction || data;

            return {
                success: true,
                primary_disease: prediction.primary_disease || prediction.disease || prediction.primaryDisease || 'Évaluation en attente',
                confidence: Number(prediction.confidence ?? 0.5),
                top_3_diseases: prediction.top_3_diseases || prediction.topDiseases || []
            };
        } catch (error) {
            console.error('Erreur lors du diagnostic:', error);
            return APIClient.getMockDiagnosis(symptoms);
        }
    }

    /**
     * Obtenir le score de risque
     * @param {string} disease - Maladie
     * @param {Array<string>} symptoms - Symptômes
     * @returns {Promise} Score de risque
     */
    static async getRiskScore(disease, symptoms) {
        try {
            const response = await fetch(`${API_BASE_URL}/diagnostic/risk-level`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ disease, symptoms })
            });

            if (!response.ok) {
                throw new Error(`Erreur API: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Erreur lors du calcul du risque:', error);
            return APIClient.getMockRiskScore();
        }
    }

    /**
     * Obtenir les recommandations
     * @param {string} disease - Maladie diagnostiquée
     * @param {number} riskScore - Score de risque
     * @returns {Promise} Recommandations
     */
    static async getRecommendations(disease, riskScore) {
        try {
            const response = await fetch(`${API_BASE_URL}/diagnostic/recommendations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ disease, risk_score: riskScore })
            });

            if (!response.ok) {
                throw new Error(`Erreur API: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Erreur lors de la récupération des recommandations:', error);
            return APIClient.getMockRecommendations(disease);
        }
    }

    /**
     * Réponses factices pour développement (quand l'API n'est pas disponible)
     */
    static getMockResponse(symptoms) {
        return {
            success: true,
            message: 'Message reçu avec succès',
            symptoms: symptoms.split(',').map(s => s.trim())
        };
    }

    static getMockDiagnosis(symptoms) {
        const mockDiseases = {
            'toux': { disease: 'Grippe', confidence: 0.75 },
            'fièvre': { disease: 'COVID-19', confidence: 0.82 },
            'mal à la tête': { disease: 'Migraine', confidence: 0.68 },
            'nausée': { disease: 'Gastro-entérite', confidence: 0.71 },
            'fatigue': { disease: 'Rhume', confidence: 0.65 }
        };

        const symptomText = Array.isArray(symptoms)
            ? symptoms.join(' ')
            : String(symptoms ?? '');
        const lowerText = symptomText.toLowerCase();
        let bestMatch = { disease: 'Grippe', confidence: 0.70 };

        for (const [key, value] of Object.entries(mockDiseases)) {
            if (lowerText.includes(key)) {
                bestMatch = value;
                break;
            }
        }

        return {
            success: true,
            primary_disease: bestMatch.disease,
            confidence: bestMatch.confidence,
            top_3_diseases: [
                { disease: bestMatch.disease, probability: bestMatch.confidence },
                { disease: 'Rhume', probability: 0.45 },
                { disease: 'Allergie', probability: 0.32 }
            ]
        };
    }

    static getMockRiskScore() {
        return {
            success: true,
            risk_score: Math.random() * 0.8 + 0.2,
            risk_level: ['BASSE', 'MODÉRÉE', 'ÉLEVÉE'][Math.floor(Math.random() * 3)]
        };
    }

    static getMockRecommendations(disease) {
        const recommendations = {
            'COVID-19': [
                'Isolement recommandé pendant 7 jours minimum',
                'Effectuer un test COVID pour confirmation',
                'Prendre des antipyrétiques si nécessaire',
                'Rester au repos complet'
            ],
            'Grippe': [
                'Repos complet pour 24-48h',
                'Boire beaucoup de liquides',
                'Consulter un pharmacien pour antiviraux',
                'Éviter le contact avec d\'autres personnes'
            ],
            'Rhume': [
                'Repos de 24h minimum',
                'Hydratation abondante',
                'Inhalation de vapeur chaude',
                'Surveillance des symptômes'
            ],
            'Gastro-entérite': [
                'Hydratation régulière par petites quantités',
                'Repos complet',
                'Régime léger (riz, pain grillé)',
                'Consulter si diarrhée persiste > 3 jours'
            ]
        };

        return {
            success: true,
            recommendations: recommendations[disease] || [
                'Consulter un médecin',
                'Prendre du repos',
                'Rester hydraté',
                'Surveiller les symptômes'
            ]
        };
    }
}

// Exporter pour utilisation dans d'autres modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIClient;
}
