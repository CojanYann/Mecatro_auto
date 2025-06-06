// This file contains the JavaScript code for the application. It handles the interactive features, such as updating the user interface, managing WebSocket connections, and simulating sensor data.

const activityLog = document.getElementById('activity-log');
const jsonLogContainer = document.getElementById('json-log');
const modeButton = document.getElementById('mode-btn');
const speedSlider = document.getElementById('speed-slider');
const speedValue = document.getElementById('speed-value');

let jsonLogData = [];
let isManualMode = true; // Par défaut, le mode est manuel

// Fonction pour ajouter une entrée JSON au log sans timestamp
function addJsonLogEntry(action, description) {
    const logEntry = { action, description };
    jsonLogData.push(logEntry);

    // Mettre à jour l'affichage
    jsonLogContainer.textContent = JSON.stringify(jsonLogData, null, 2);
}

// Fonction pour afficher les logs dans la console
function addLogEntry(message) {
    console.log(message);
    // Vous pouvez aussi l'afficher dans un div si besoin
}

// Fonction pour envoyer une commande et afficher dans le terminal
function executeAction(action, description) {
    // Ajouter immédiatement l'entrée au log JSON
    addJsonLogEntry(action, description);

    fetch(action, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {
                addLogEntry(`Action réussie : ${description}`);
                fetchAndDisplayGpsCoords(); // <-- Ajout ici
            } else {
                addLogEntry(`Erreur lors de l'action : ${description}`);
            }
        })
        .catch(error => {
            addLogEntry(`Erreur réseau : ${description}`);
        });
}

// Ajouter des écouteurs pour les boutons
document.getElementById('pickup-btn').addEventListener('click', function() {
    executeAction('/action/ramasser', 'Lancer ramassage');
});

document.getElementById('empty-btn').addEventListener('click', function() {
    executeAction('/action/vider', 'Vider le bac');
});

document.getElementById('base-btn').addEventListener('click', function() {
    executeAction('/action/retour', 'Retour à la base');
});

// Ajouter des écouteurs pour les touches directionnelles
document.getElementById('forward-btn').addEventListener('click', function() {
    executeAction('/api/move/forward', 'Avancer');
});

document.getElementById('backward-btn').addEventListener('click', function() {
    executeAction('/api/move/backward', 'Reculer');
});

document.getElementById('left-btn').addEventListener('click', function() {
    executeAction('/api/move/left', 'Tourner à gauche');
});

document.getElementById('right-btn').addEventListener('click', function() {
    executeAction('/api/move/right', 'Tourner à droite');
});

document.getElementById('stop-btn').addEventListener('click', function() {
    executeAction('/api/move/stop', 'Stop');
});


// Fonction pour basculer entre les modes manu  el et automatique
modeButton.addEventListener('click', function() {
    if (isManualMode) {
        executeAction('/api/mode/auto', 'Passer en mode automatique');
        modeButton.textContent = 'Auto';
        isManualMode = false;
    } else {
        executeAction('/api/mode/manual', 'Passer en mode manuel');
        modeButton.textContent = 'Manuel';
        isManualMode = true;
    }
});

// Fonction pour envoyer la vitesse au format JSON POST {speed: valeur}
function postSpeed(speed) {
    fetch('/api/speed', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ speed: speed })
    })
    .then(response => response.json())
    .then(data => {
        addLogEntry(`Vitesse envoyée : ${speed} (réponse: ${JSON.stringify(data)})`);
    })
    .catch(error => {
        addLogEntry(`Erreur lors de l'envoi de la vitesse : ${error}`);
    });
}

// Met à jour l'affichage en temps réel
speedSlider.addEventListener('input', function() {
    const speed = 100 - speedSlider.value;
    speedValue.textContent = `${speed}%`;
});

// Publie la valeur sur l'API quand on lâche le slider
speedSlider.addEventListener('change', function() {
    const speed = 100 - speedSlider.value;
    postSpeed(speed);
});
