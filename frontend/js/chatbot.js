/**
 * Module Chatbot - Gestion logique du chatbot
 */

class Chatbot {
    constructor() {
        this.messages = [];
        this.currentDiagnosis = null;
    }

    /**
     * Ajoute un message à l'historique
     * @param {string} text - Texte du message
     * @param {string} sender - 'user' ou 'system'
     */
    addMessage(text, sender = 'system') {
        const message = {
            id: Date.now(),
            text: text,
            sender: sender,
            timestamp: new Date()
        };

        this.messages.push(message);
        return message;
    }

    /**
     * Traite un message utilisateur
     * @param {string} userInput - Entrée utilisateur
     * @returns {Promise<Object>} Résultat du diagnostic
     */
    async processUserInput(userInput) {
        if (!userInput.trim()) {
            return null;
        }

        // Ajouter le message utilisateur
        this.addMessage(userInput, 'user');

        try {
            // Montrer le spinner
            document.getElementById('loadingSpinner').style.display = 'flex';

            // 1. Envoyer les symptômes
            const response = await APIClient.sendSymptoms(userInput);
            
            // 2. Obtenir le diagnostic
            const symptoms = this.extractSymptoms(userInput);
            const diagnosis = await APIClient.getDiagnosis(symptoms);

            // 3. Obtenir le score de risque
            const riskData = await APIClient.getRiskScore(diagnosis.primary_disease, symptoms);

            // 4. Obtenir les recommandations
            const recommendations = await APIClient.getRecommendations(
                diagnosis.primary_disease,
                riskData.risk_score
            );

            // Composer la réponse du système
            const systemMessage = this.formatDiagnosisResponse(diagnosis, riskData, recommendations);
            this.addMessage(systemMessage, 'system');

            // Stocker le diagnostic actuel
            this.currentDiagnosis = {
                diagnosis,
                riskData,
                recommendations,
                symptoms
            };

            return this.currentDiagnosis;

        } catch (error) {
            console.error('Erreur lors du traitement:', error);
            this.addMessage('Erreur lors du traitement. Veuillez réessayer.', 'system');
            return null;
        } finally {
            // Cacher le spinner
            document.getElementById('loadingSpinner').style.display = 'none';
        }
    }

    /**
     * Extrait les symptômes du texte
     * @param {string} text - Texte à traiter
     * @returns {Array<string>} Symptômes extraits
     */
    extractSymptoms(text) {
        // Implémentation simple - à améliorer avec NLP
        const symptomPatterns = [
            'mal à la tête', 'migraine', 'céphalée',
            'fièvre', 'température',
            'toux', 'quinte',
            'nausée', 'vomissement',
            'fatigue', 'faiblesse', 'épuisement',
            'rhume', 'congestion',
            'douleur', 'douleur musculaire',
            'allergie', 'éternuement',
            'diarrhée', 'constipation',
            'mal de gorge', 'angine',
            'insomnie', 'sommeil',
            'anxiété', 'stress',
            'vertiges', 'étourdissement'
        ];

        const lowerText = text.toLowerCase();
        const symptoms = symptomPatterns.filter(pattern => 
            lowerText.includes(pattern)
        );

        return symptoms.length > 0 ? symptoms : ['symptômes généraux'];
    }

    /**
     * Formate la réponse du diagnostic
     * @param {Object} diagnosis - Diagnostic
     * @param {Object} riskData - Données de risque
     * @param {Object} recommendations - Recommandations
     * @returns {string} Message formaté
     */
    formatDiagnosisResponse(diagnosis, riskData, recommendations) {
        let response = `📋 **Analyse Complète**\n\n`;
        
        response += `🔍 **Diagnostic Principal:** ${diagnosis.primary_disease}\n`;
        response += `Confiance: ${(diagnosis.confidence * 100).toFixed(1)}%\n\n`;
        
        response += `⚠️ **Niveau de Risque:** ${riskData.risk_level}\n`;
        response += `Score: ${(riskData.risk_score * 100).toFixed(1)}%\n\n`;
        
        response += `✅ **Recommandations:**\n`;
        if (Array.isArray(recommendations.recommendations)) {
            recommendations.recommendations.forEach((rec, index) => {
                response += `${index + 1}. ${this.formatRecommendationText(rec)}\n`;
            });
        }
        
        response += `\n⚠️ **Important:** Ceci est une évaluation préliminaire uniquement. Consultez toujours un professionnel de santé qualifié.`;
        
        return response;
    }

    /**
     * Récupère tous les messages
     * @returns {Array} Messages
     */
    formatRecommendationText(rec) {
        if (typeof rec === 'string') {
            return rec;
        }

        if (rec && typeof rec === 'object') {
            const action = rec.action || rec.title || rec.recommendation || '';
            const detail = rec.detail || rec.description || '';
            return detail ? `${action} - ${detail}` : action;
        }

        return String(rec ?? '');
    }

    getMessages() {
        return this.messages;
    }

    /**
     * Efface l'historique
     */
    clearHistory() {
        this.messages = [];
        this.currentDiagnosis = null;
    }
}

// Exporter pour utilisation globale
window.Chatbot = Chatbot;
