// static/email.js - Gestion des emails (version corrigée)

let currentEmailId = null;
let emails = [];

document.addEventListener('DOMContentLoaded', function() {
    console.log("📧 Email Dashboard chargé");
    loadEmails();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('refreshBtn').addEventListener('click', loadEmails);
    document.getElementById('processAllBtn').addEventListener('click', processAllEmails);
    document.getElementById('addEmailBtn').addEventListener('click', showAddEmailModal);
    document.getElementById('clearAllBtn').addEventListener('click', clearAllEmails);
    document.getElementById('detailCloseBtn').addEventListener('click', closeDetail);
    document.getElementById('detailProcessBtn').addEventListener('click', () => processEmail(currentEmailId));
    document.getElementById('detailGenerateBtn').addEventListener('click', () => generateResponse(currentEmailId));
    document.getElementById('detailDeleteBtn').addEventListener('click', () => deleteEmail(currentEmailId));
}

// ============================================
// CHARGER LES EMAILS (GET /api/emails/)
// ============================================
function loadEmails() {
    console.log("🔄 Chargement des emails...");
    fetch('/api/emails/')
        .then(res => res.json())
        .then(data => {
            emails = data;
            renderEmails(emails);
            updateStats(emails);
        })
        .catch(err => console.error("❌ Erreur chargement:", err));
}

// ============================================
// AFFICHER LA LISTE
// ============================================
function renderEmails(emails) {
    const container = document.getElementById('emailListContainer');
    if (!emails || emails.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">📭</div>
                <p>Aucun email</p>
            </div>
        `;
        return;
    }

    let html = '';
    emails.forEach(email => {
        const isProcessed = email.is_processed;
        const urgencyClass = email.urgency === 'Haute' ? 'badge-urgence-haute' :
                             email.urgency === 'Moyenne' ? 'badge-urgence-moyenne' :
                             'badge-urgence-basse';
        const statusClass = isProcessed ? 'badge-traite' : 'badge-non-traite';
        const statusText = isProcessed ? '✅ Traité' : '⏳ En attente';

        html += `
            <div class="email-item" data-id="${email.id}" onclick="openDetail('${email.id}')">
                <div class="info">
                    <div class="from">${email.from}</div>
                    <div class="subject">${email.subject}</div>
                    <div class="summary">${email.summary || email.body.substring(0, 80)}${email.body.length > 80 ? '...' : ''}</div>
                </div>
                <div style="display:flex; gap:5px; flex-wrap:wrap;">
                    <span class="badge ${urgencyClass}">⚠️ ${email.urgency}</span>
                    <span class="badge badge-categorie">📂 ${email.category}</span>
                    <span class="badge ${statusClass}">${statusText}</span>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

// ============================================
// STATISTIQUES
// ============================================
function updateStats(emails) {
    const total = emails.length;
    const unprocessed = emails.filter(e => !e.is_processed).length;
    const urgent = emails.filter(e => e.urgency === 'Haute').length;
    const processed = emails.filter(e => e.is_processed).length;

    document.getElementById('totalCount').textContent = total;
    document.getElementById('unprocessedCount').textContent = unprocessed;
    document.getElementById('urgentCount').textContent = urgent;
    document.getElementById('processedCount').textContent = processed;
}

// ============================================
// OUVRIR LE DÉTAIL D'UN EMAIL
// ============================================
function openDetail(emailId) {
    currentEmailId = emailId;
    const email = emails.find(e => e.id === emailId);
    if (!email) return;

    const detail = document.getElementById('emailDetail');
    detail.style.display = 'block';

    document.getElementById('detailFrom').textContent = email.from;
    document.getElementById('detailSubject').textContent = email.subject;
    document.getElementById('detailBody').textContent = email.body;

    const urgencyClass = email.urgency === 'Haute' ? 'badge-urgence-haute' :
                         email.urgency === 'Moyenne' ? 'badge-urgence-moyenne' :
                         'badge-urgence-basse';
    document.getElementById('detailBadgeUrgency').textContent = '⚠️ ' + email.urgency;
    document.getElementById('detailBadgeUrgency').className = `badge ${urgencyClass}`;
    document.getElementById('detailBadgeCategory').textContent = '📂 ' + email.category;
    document.getElementById('detailBadgeAction').textContent = '🎯 ' + email.action;

    const statusClass = email.is_processed ? 'badge-traite' : 'badge-non-traite';
    document.getElementById('detailBadgeStatus').textContent = email.is_processed ? '✅ Traité' : '⏳ En attente';
    document.getElementById('detailBadgeStatus').className = `badge ${statusClass}`;

    const responseDiv = document.getElementById('detailResponse');
    if (email.response) {
        responseDiv.style.display = 'block';
        document.getElementById('detailResponseText').textContent = email.response;
    } else {
        responseDiv.style.display = 'none';
    }

    detail.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function closeDetail() {
    document.getElementById('emailDetail').style.display = 'none';
    currentEmailId = null;
}

// ============================================
// ANALYSER UN EMAIL (POST /api/email-ai/process)
// ============================================
function processEmail(emailId) {
    if (!emailId) return;
    const email = emails.find(e => e.id === emailId);
    if (!email) return;

    fetch('/api/email-ai/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            email_id: emailId,
            content: email.body,
            subject: email.subject,
            from: email.from
        })
    })
    .then(res => res.json())
    .then(data => {
        console.log("🔍 Analyse terminée:", data);
        loadEmails();
        if (currentEmailId === emailId) {
            openDetail(emailId);
        }
    })
    .catch(err => console.error("❌ Erreur analyse:", err));
}

// ============================================
// ANALYSER TOUS LES EMAILS
// ============================================
function processAllEmails() {
    const unprocessed = emails.filter(e => !e.is_processed);
    if (unprocessed.length === 0) {
        alert("✅ Tous les emails sont déjà traités.");
        return;
    }

    if (!confirm(`Analyser ${unprocessed.length} email(s) ?`)) return;

    unprocessed.forEach(email => {
        fetch('/api/email-ai/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email_id: email.id,
                content: email.body,
                subject: email.subject,
                from: email.from
            })
        })
        .then(res => res.json())
        .then(() => {
            loadEmails();
        })
        .catch(err => console.error("❌ Erreur analyse:", err));
    });
}

// ============================================
// GÉNÉRER UNE RÉPONSE (POST /api/email-ai/generate-response)
// ============================================
function generateResponse(emailId) {
    if (!emailId) return;
    const email = emails.find(e => e.id === emailId);
    if (!email) return;

    fetch('/api/email-ai/generate-response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            email_id: emailId,
            content: email.body,
            category: email.category
        })
    })
    .then(res => res.json())
    .then(data => {
        console.log("✍️ Réponse générée:", data);
        const emailObj = emails.find(e => e.id === emailId);
        if (emailObj) emailObj.response = data.response;
        if (currentEmailId === emailId) {
            openDetail(emailId);
        }
        loadEmails();
    })
    .catch(err => console.error("❌ Erreur génération:", err));
}

// ============================================
// AJOUTER UN EMAIL (POST /api/emails/create)
// ============================================
function showAddEmailModal() {
    const from = prompt("📧 De (expéditeur) :");
    if (!from) return;
    const subject = prompt("📝 Sujet :") || "Sans objet";
    const body = prompt("📄 Contenu :");
    if (!body) return;

    fetch('/api/emails/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from, subject, body })
    })
    .then(res => res.json())
    .then(() => {
        loadEmails();
    })
    .catch(err => console.error("❌ Erreur création:", err));
}

// ============================================
// SUPPRIMER UN EMAIL (DELETE /api/emails/<id>)
// ============================================
function deleteEmail(emailId) {
    if (!emailId) return;
    if (!confirm("🗑️ Supprimer cet email ?")) return;

    fetch(`/api/emails/${emailId}`, { method: 'DELETE' })
        .then(() => {
            closeDetail();
            loadEmails();
        })
        .catch(err => console.error("❌ Erreur suppression:", err));
}

// ============================================
// SUPPRIMER TOUS LES EMAILS
// ============================================
function clearAllEmails() {
    if (!confirm("🗑️ Supprimer TOUS les emails ?")) return;
    emails.forEach(email => {
        fetch(`/api/emails/${email.id}`, { method: 'DELETE' })
            .catch(err => console.error("❌ Erreur suppression:", err));
    });
    setTimeout(loadEmails, 1000);
}