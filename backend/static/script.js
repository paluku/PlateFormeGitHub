
  <!-- ============================================= -->
    <!-- JAVASCRIPT COMPLET (UN SEUL FICHIER) -->
    <!-- ============================================= -->
   
        console.log("🚀 JavaScript intégré chargé !");

        const agentDescriptions = {
            'base': { name: 'Base Agent', desc: 'Agent de base - Réponses simples' },
            'echo': { name: 'Echo Agent', desc: 'Écho et analyse des messages' },
            'assistant': { name: 'Assistant Agent', desc: 'Assistant conversationnel avec IA (Ollama)' },
            'specialist': { name: 'Specialist Agent', desc: 'Agent spécialisé avec IA (Ollama)' },
            'collaborative': { name: 'Collaborative Agent', desc: 'Coordination multi-agents avec IA (Ollama)' },
			 'filereader': { name: 'FileReader Agent', desc: '📄 Lit et analyse les fichiers' },
            'filecreator': { name: 'FileCreator Agent', desc: '📝 Crée et exporte des fichiers (TXT, CSV, JSON, HTML, MD, PY, XML)' },
            'email_agent': { name: '📧 Email Agent', desc: 'Analyse et réponse automatique des emails clients' }
		
		};

        let currentAgent = 'base';
        let currentConversation = 1;

        function updateAgentInfo(agentKey) {
            const info = agentDescriptions[agentKey];
            document.getElementById('agentName').textContent = `🤖 ${info.name}`;
            document.getElementById('agentDescription').textContent = info.desc;
            console.log("📝 Agent mis à jour:", agentKey);
        }

        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
                this.classList.add('active');
                currentAgent = this.dataset.agent;
                updateAgentInfo(currentAgent);
                loadConversationHistory(currentConversation);
            });
        });

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

        function addMessage(role, content, agentName = null) {
            const messages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            if (role === 'user') {
                messageDiv.innerHTML = `<div class="message-content">${content}</div>`;
            } else {
                const name = agentName || currentAgent;
                const info = agentDescriptions[name] || agentDescriptions['base'];
                messageDiv.innerHTML = `
                    <div class="message-content">
                        <div class="message-agent-name">🤖 ${info.name}</div>
                        ${content}
                    </div>
                `;
            }
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message) return;
            console.log("💬 Message:", message);
            addMessage('user', message);
            input.value = '';
            
            const loadingMsg = document.createElement('div');
            loadingMsg.className = 'message agent';
            loadingMsg.id = 'loadingMsg';
            loadingMsg.innerHTML = `
                <div class="message-content">
                    <div class="message-agent-name">🤖 ${agentDescriptions[currentAgent].name}</div>
                    <em>⏳ Réflexion en cours...</em>
                </div>
            `;
            document.getElementById('chatMessages').appendChild(loadingMsg);
            
            fetch('/api/chat/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    agent: currentAgent,
                    conversation_id: currentConversation
                })
            })
            .then(response => {
                console.log("📥 Status:", response.status);
                return response.json();
            })
            .then(data => {
                console.log("📦 Données reçues:", data);
                const loadingEl = document.getElementById('loadingMsg');
                if (loadingEl) loadingEl.remove();
                addMessage('agent', data.response, currentAgent);
            })
            .catch(error => {
                console.error('❌ Erreur:', error);
                const loadingEl = document.getElementById('loadingMsg');
                if (loadingEl) loadingEl.remove();
                addMessage('agent', `⚠️ Erreur: ${error.message}`, currentAgent);
            });
        }

        document.getElementById('sendBtn').addEventListener('click', sendMessage);
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });

        document.addEventListener('DOMContentLoaded', function() {
            console.log("🌐 DOM chargé !");
            updateAgentInfo('base');
            loadConversationHistory(1);
            console.log("✅ Initialisation terminée !");
        });
		
		///////////////////////////////////////////////////////////////////////////////
		document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        this.classList.add('active');
        currentAgent = this.dataset.agent;
        updateAgentInfo(currentAgent);
        loadConversationHistory(currentConversation);
        
        // Si c'est FileReader, montrer la zone
        if (currentAgent === 'filereader') {
            toggleFileReader(true);
        } else {
            toggleFileReader(false);
        }
    });
});
	


// =============================================
// GESTION DE L'UPLOAD
// =============================================
// =============================================
// GESTION DE L'UPLOAD ET LECTURE
// =============================================

let currentFileName = '';

// Afficher/masquer la zone d'upload
function toggleUploadArea(agentKey) {
    const uploadArea = document.getElementById('uploadArea');
    if (agentKey === 'filereader') {
        uploadArea.style.display = 'block';
    } else {
        uploadArea.style.display = 'none';
        document.getElementById('fileContent').style.display = 'none';
    }
}

// Modifier updateAgentInfo
const originalUpdate = updateAgentInfo;
updateAgentInfo = function(agentKey) {
    originalUpdate(agentKey);
    toggleUploadArea(agentKey);
};

// Upload de fichier
document.getElementById('uploadBtn').addEventListener('click', function() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    const status = document.getElementById('uploadStatus');
    
    if (!file) {
        status.textContent = '⚠️ Sélectionne un fichier !';
        status.style.color = '#ff6b6b';
        return;
    }
    
    status.textContent = '⏳ Upload en cours...';
    status.style.color = '#ff922b';
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            status.textContent = '❌ ' + data.error;
            status.style.color = '#ff6b6b';
        } else {
            currentFileName = data.filename;
            status.textContent = '✅ ' + data.message;
            status.style.color = '#28a745';
            
            // Afficher le contenu automatiquement
            readFileContent(data.filename);
        }
    })
    .catch(error => {
        status.textContent = '❌ Erreur: ' + error.message;
        status.style.color = '#ff6b6b';
    });
});

// Lire le fichier
document.getElementById('readBtn').addEventListener('click', function() {
    const fileInput = document.getElementById('fileInput');
    const status = document.getElementById('uploadStatus');
    
    let filename = currentFileName;
    
    if (!filename && fileInput.files.length > 0) {
        filename = fileInput.files[0].name;
    }
    
    if (!filename) {
        status.textContent = '⚠️ Upload un fichier d\'abord !';
        status.style.color = '#ff6b6b';
        return;
    }
    
    readFileContent(filename);
});

function readFileContent(filename) {
    const status = document.getElementById('uploadStatus');
    const contentDiv = document.getElementById('fileContent');
    
    status.textContent = '⏳ Lecture en cours...';
    status.style.color = '#ff922b';
    
    fetch(`/api/uploads/${filename}`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            status.textContent = '❌ ' + data.error;
            status.style.color = '#ff6b6b';
            contentDiv.style.display = 'none';
        } else {
            status.textContent = '✅ Fichier lu avec succès';
            status.style.color = '#28a745';
            contentDiv.style.display = 'block';
            contentDiv.textContent = data.content || 'Contenu vide';
        }
    })
    .catch(error => {
        status.textContent = '❌ Erreur: ' + error.message;
        status.style.color = '#ff6b6b';
        contentDiv.style.display = 'none';
    });
}

// Effacer le contenu
document.getElementById('clearFileBtn').addEventListener('click', function() {
    document.getElementById('fileContent').style.display = 'none';
    document.getElementById('fileContent').textContent = '';
    document.getElementById('uploadStatus').textContent = '';
    document.getElementById('fileInput').value = '';
    currentFileName = '';
});

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    toggleUploadArea('base');
});

/////////////////////////////////////////////////////////////////////

// =============================================
// LISTER LES FICHIERS
// =============================================

document.getElementById('listBtn').addEventListener('click', function() {
    listUploadedFiles();
});

function listUploadedFiles() {
    const status = document.getElementById('uploadStatus');
    const listDiv = document.getElementById('fileListDiv');
    const contentDiv = document.getElementById('fileListContent');
    
    status.textContent = '⏳ Chargement...';
    status.style.color = '#ff922b';
    
    fetch('/api/uploads')
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            status.textContent = '❌ ' + data.error;
            status.style.color = '#ff6b6b';
            listDiv.style.display = 'none';
            return;
        }
        
        listDiv.style.display = 'block';
        status.textContent = `📁 ${data.count} fichier(s) trouvé(s)`;
        status.style.color = '#17a2b8';
        
        if (data.files.length === 0) {
            contentDiv.innerHTML = '<em style="color: #888;">Aucun fichier uploadé</em>';
            return;
        }
        
        let html = '';
        data.files.forEach(f => {
            const size = (f.size / 1024).toFixed(1);
            const date = new Date(f.modified * 1000);
            const dateStr = date.toLocaleString();
            html += `
                <div class="file-item">
                    <span class="file-name">📄 ${f.name}</span>
                    <span class="file-size">${size} KB</span>
                    <span class="file-date">${dateStr}</span>
                </div>
            `;
        });
        
        contentDiv.innerHTML = html;
    })
    .catch(error => {
        status.textContent = '❌ Erreur: ' + error.message;
        status.style.color = '#ff6b6b';
        listDiv.style.display = 'none';
    });
}

async function downloadFile(filename) {
    try {
        const decodedFilename = decodeURIComponent(filename);
        console.log('⬇️ Téléchargement:', decodedFilename);
        
        // Utiliser fetch pour obtenir le fichier
        const response = await fetch(`/api/files/${encodeURIComponent(decodedFilename)}`);
        
        console.log('📥 Status:', response.status);
        console.log('📥 Content-Type:', response.headers.get('content-type'));
        
        if (response.ok) {
            // Récupérer le blob
            const blob = await response.blob();
            
            // Créer un lien de téléchargement
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = decodedFilename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            document.getElementById('downloadStatus').innerHTML = `✅ Téléchargement de ${decodedFilename} terminé !`;
            document.getElementById('downloadStatus').style.color = '#28a745';
            
            setTimeout(() => {
                document.getElementById('downloadStatus').innerHTML = '';
            }, 3000);
        } else {
            const text = await response.text();
            console.error('❌ Erreur réponse:', text);
            document.getElementById('downloadStatus').innerHTML = `❌ Erreur: ${response.status}`;
            document.getElementById('downloadStatus').style.color = '#dc3545';
        }
    } catch (error) {
        console.error('❌ Erreur:', error);
        document.getElementById('downloadStatus').innerHTML = `❌ Erreur: ${error.message}`;
        document.getElementById('downloadStatus').style.color = '#dc3545';
    }
}