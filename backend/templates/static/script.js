// static/script.js - Version complète avec API Flask
console.log("🚀 script.js chargé avec succès !");

const agentDescriptions = {
    'base': { name: 'Base Agent', desc: 'Agent de base - Réponses simples' },
    'echo': { name: 'Echo Agent', desc: 'Écho et analyse des messages' },
    'assistant': { name: 'Assistant Agent', desc: 'Assistant conversationnel avec IA (Ollama)' },
    'specialist': { name: 'Specialist Agent', desc: 'Agent spécialisé avec IA (Ollama)' },
    'collaborative': { name: 'Collaborative Agent', desc: 'Coordination multi-agents avec IA (Ollama)' },
    'email_agent': { name: '📧 Email Agent', desc: 'Analyse et réponse automatique des emails clients' }


};

let currentAgent = 'base';
let currentConversation = 1;

// Navigation entre les agents
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        console.log("🔄 Changement d'agent vers:", this.dataset.agent);
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        this.classList.add('active');
        currentAgent = this.dataset.agent;
        updateAgentInfo(currentAgent);
        loadConversationHistory(currentConversation);
    });
});

function updateAgentInfo(agentKey) {
    const info = agentDescriptions[agentKey];
    document.getElementById('agentName').textContent = `🤖 ${info.name}`;
    document.getElementById('agentDescription').textContent = info.desc;
    console.log("📝 Agent mis à jour:", agentKey);
}

function loadConversationHistory(convId) {
    console.log("📜 Chargement de l'historique:", convId);
    fetch(`/api/chat/history/${convId}`)
        .then(response => response.json())
        .then(messages => {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = '';
            
            if (messages.length === 0) {
                const welcomeMsg = document.createElement('div');
                welcomeMsg.className = 'message agent';
                welcomeMsg.innerHTML = `
                    <div class="message-content">
                        <div class="message-agent-name">🤖 ${agentDescriptions[currentAgent].name}</div>
                        Nouvelle conversation ! Envoyez-moi un message.
                    </div>
                `;
                chatMessages.appendChild(welcomeMsg);
            } else {
                messages.forEach(msg => {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${msg.role === 'user' ? 'user' : 'agent'}`;
                    const content = msg.role === 'user' 
                        ? msg.content 
                        : `<div class="message-agent-name">🤖 ${agentDescriptions[currentAgent].name}</div>${msg.content}`;
                    messageDiv.innerHTML = `<div class="message-content">${content}</div>`;
                    chatMessages.appendChild(messageDiv);
                });
            }
            chatMessages.scrollTop = chatMessages.scrollHeight;
        })
        .catch(error => console.error('Erreur:', error));
}

// Envoi de message - Bouton
document.getElementById('sendBtn').addEventListener('click', function() {
    console.log("🖱️ Clic sur le bouton Envoyer !");
    sendMessage();
});

// Envoi de message - Touche Entrée
document.getElementById('messageInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        console.log("⌨️ Touche Entrée pressée !");
        sendMessage();
    }
});

// Fonction principale d'envoi de message
function sendMessage() {
    console.log("📤 sendMessage() appelée !");
    
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    console.log("💬 Message:", message);
    
    if (!message) {
        console.log("⚠️ Message vide, ignoré");
        return;
    }
    
    const messages = document.getElementById('chatMessages');
    
    // Ajouter le message de l'utilisateur
    const userMsg = document.createElement('div');
    userMsg.className = 'message user';
    userMsg.innerHTML = `<div class="message-content">${message}</div>`;
    messages.appendChild(userMsg);
    
    input.value = '';
    messages.scrollTop = messages.scrollHeight;
    
    // Afficher "en cours..."
    const loadingMsg = document.createElement('div');
    loadingMsg.className = 'message agent';
    loadingMsg.id = 'loadingMsg';
    loadingMsg.innerHTML = `
        <div class="message-content">
            <div class="message-agent-name">🤖 ${agentDescriptions[currentAgent].name}</div>
            <em>⏳ Réflexion en cours...</em>
        </div>
    `;
    messages.appendChild(loadingMsg);
    messages.scrollTop = messages.scrollHeight;
    
    console.log("📡 Envoi à l'API:", { message, agent: currentAgent, conversation_id: currentConversation });
    
    // =============================================
    // APPEL À L'API FLASK (le coeur du système)
    // =============================================
    fetch('/api/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            agent: currentAgent,
            conversation_id: currentConversation
        })
    })
    .then(response => {
        console.log("📥 Réponse API reçue, status:", response.status);
        return response.json();
    })
    .then(data => {
        console.log("📦 Données reçues:", data);
        
        // Supprimer le message de chargement
        const loadingEl = document.getElementById('loadingMsg');
        if (loadingEl) loadingEl.remove();
        
        // Ajouter la réponse de l'agent
        const agentMsg = document.createElement('div');
        agentMsg.className = 'message agent';
        agentMsg.innerHTML = `
            <div class="message-content">
                <div class="message-agent-name">🤖 ${agentDescriptions[currentAgent].name}</div>
                ${data.response}
            </div>
        `;
        messages.appendChild(agentMsg);
        messages.scrollTop = messages.scrollHeight;
        
        console.log("✅ Message affiché !");
    })
    .catch(error => {
        console.error('❌ Erreur:', error);
        const loadingEl = document.getElementById('loadingMsg');
        if (loadingEl) loadingEl.remove();
        
        const errorMsg = document.createElement('div');
        errorMsg.className = 'message agent';
        errorMsg.innerHTML = `
            <div class="message-content">
                <div class="message-agent-name">⚠️ Erreur</div>
                Impossible de contacter le serveur: ${error.message}
            </div>
        `;
        messages.appendChild(errorMsg);
        messages.scrollTop = messages.scrollHeight;
    });
}

// Charger l'historique au démarrage
document.addEventListener('DOMContentLoaded', function() {
    console.log("🌐 DOM chargé !");
    updateAgentInfo('base');
    loadConversationHistory(1);
    console.log("✅ Initialisation terminée !");
});