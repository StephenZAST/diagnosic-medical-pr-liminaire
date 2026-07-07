/**
 * Main.js - Logique principale du frontend
 */

let chatbot = null;

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    chatbot = new Chatbot();
    setupEventListeners();
    displayWelcomeMessage();
});

/**
 * Configure les écouteurs d'événements
 */
function setupEventListeners() {
    const sendBtn = document.getElementById('sendBtn');
    const symptomInput = document.getElementById('symptomInput');

    // Bouton Envoyer
    sendBtn.addEventListener('click', () => {
        handleSendMessage();
    });

    // Entrée au clavier (Entrée)
    symptomInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
}

/**
 * Traite l'envoi d'un message
 */
async function handleSendMessage() {
    const input = document.getElementById('symptomInput');
    const userInput = input.value.trim();

    if (!userInput) {
        return;
    }

    // Ajouter le message à l'affichage
    addMessageToUI(userInput, 'user');
    input.value = '';
    input.focus();

    // Traiter l'entrée
    const result = await chatbot.processUserInput(userInput);

    if (result) {
        // Afficher les résultats
        displayDiagnosisResults(result);
        
        // Ajouter le message système
        const messages = chatbot.getMessages();
        if (messages.length > 0) {
            const lastMessage = messages[messages.length - 1];
            addMessageToUI(lastMessage.text, 'system');
        }
    }

    // Scroll au bas
    scrollToBottom();
}

/**
 * Ajoute un message à l'interface
 * @param {string} text - Texte du message
 * @param {string} sender - 'user' ou 'system'
 */
function addMessageToUI(text, sender) {
    const container = document.getElementById('messagesContainer');
    
    const messageEl = document.createElement('div');
    messageEl.className = `message ${sender}-message`;
    
    // Traiter le texte (markdown basique)
    let formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/__(.*?)__/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
    
    messageEl.innerHTML = `<p>${formattedText}</p>`;
    container.appendChild(messageEl);
    
    scrollToBottom();
}

/**
 * Affiche les résultats du diagnostic
 * @param {Object} result - Résultat du diagnostic
 */
function displayDiagnosisResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    const diagnosis = result.diagnosis;
    const riskData = result.riskData;
    const recommendations = result.recommendations;
    const symptoms = result.symptoms;

    // Afficher la section résultats
    resultsSection.style.display = 'block';

    // Diagnostic principal
    document.getElementById('primaryDisease').textContent = diagnosis.primary_disease;
    
    // Confiance
    const confidence = diagnosis.confidence * 100;
    document.getElementById('confidenceScore').textContent = `Confiance: ${confidence.toFixed(1)}%`;
    document.getElementById('confidenceBar').style.width = `${confidence}%`;

    // Niveau de risque
    const riskLevel = riskData.risk_level;
    const riskBadge = document.getElementById('riskLevel');
    riskBadge.textContent = riskLevel;
    riskBadge.className = `risk-badge ${getRiskClass(riskLevel)}`;
    
    // Message de risque
    const riskMessages = {
        'BASSE': 'Le risque semble faible. Surveillance recommandée.',
        'MODÉRÉE': 'Risque modéré. Consulter un professionnel rapidement.',
        'ÉLEVÉE': 'Risque élevé. Consultation médicale urgente recommandée.'
    };
    document.getElementById('riskMessage').textContent = riskMessages[riskLevel] || 'Évaluation en cours...';

    // Diagnostics alternatifs
    const alternativesList = document.getElementById('alternativeDiseases');
    alternativesList.innerHTML = '';
    if (diagnosis.top_3_diseases && diagnosis.top_3_diseases.length > 0) {
        diagnosis.top_3_diseases.forEach((item, index) => {
            if (item.disease !== diagnosis.primary_disease) {
                const li = document.createElement('li');
                li.textContent = `${item.disease} (${(item.probability * 100).toFixed(1)}%)`;
                alternativesList.appendChild(li);
            }
        });
    }

    // Recommandations
    const recList = document.getElementById('recommendationsList');
    recList.innerHTML = '';
    if (recommendations.recommendations && recommendations.recommendations.length > 0) {
        recommendations.recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = formatRecommendationText(rec);
            recList.appendChild(li);
        });
    }

    // Symptômes identifiés
    const symptomsTags = document.getElementById('symptomsTags');
    symptomsTags.innerHTML = '';
    symptoms.forEach(symptom => {
        const tag = document.createElement('span');
        tag.className = 'symptom-tag';
        tag.textContent = symptom;
        symptomsTags.appendChild(tag);
    });

    // Scroll vers les résultats
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Récupère la classe CSS du niveau de risque
 * @param {string} riskLevel - Niveau de risque
 * @returns {string} Classe CSS
 */
function getRiskClass(riskLevel) {
    const classMap = {
        'BASSE': 'low',
        'MODÉRÉE': 'medium',
        'ÉLEVÉE': 'high'
    };
    return classMap[riskLevel] || 'medium';
}

function formatRecommendationText(rec) {
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

/**
 * Affiche le message de bienvenue
 */
function displayWelcomeMessage() {
    const container = document.getElementById('messagesContainer');
    container.innerHTML = `
        <div class="message system-message">
            <p>👋 Bienvenue dans l'Assistant Diagnostic Médical!</p>
            <p style="margin-top: 10px;">Je suis ici pour vous aider à évaluer vos symptômes et vous fournir une évaluation préliminaire.</p>
            <p style="margin-top: 10px;">💡 <strong>Comment utiliser:</strong></p>
            <ul style="margin-top: 8px; margin-left: 20px;">
                <li>Décrivez vos symptômes en détail</li>
                <li>Mentionnez depuis combien de temps vous les avez</li>
                <li>Précisez leur intensité</li>
            </ul>
            <p style="margin-top: 10px; font-size: 0.9em; opacity: 0.8;">⚠️ <strong>Important:</strong> Ceci est une évaluation préliminaire uniquement. Consultez toujours un professionnel de santé pour un diagnostic complet et un traitement approprié.</p>
        </div>
    `;
}

/**
 * Scroll vers le bas du chat
 */
function scrollToBottom() {
    const container = document.getElementById('messagesContainer');
    container.scrollTop = container.scrollHeight;
}
