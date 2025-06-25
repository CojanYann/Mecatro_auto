// This file contains the JavaScript code for the application. It handles the interactive features, such as updating the user interface, managing WebSocket connections, and simulating sensor data.

const activityLog = document.getElementById('activity-log');
const jsonLogContainer = document.getElementById('json-log');
const modeButton = document.getElementById('mode-btn');
const speedSlider = document.getElementById('speed-slider');
const speedValue = document.getElementById('speed-value');

let jsonLogData = [];
let isManualMode = true; // Par défaut, le mode est manuel
let isAudioPlaying = false;

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

// Gestion de l'IP Raspberry dynamique
const ipInput = document.getElementById('ip-input');
const ipSaveBtn = document.getElementById('ip-save-btn');
const ipStatus = document.getElementById('ip-status');

// Charger l'IP depuis le localStorage si présente
window.addEventListener('DOMContentLoaded', function() {
    const savedIp = localStorage.getItem('raspberry_ip');
    if (savedIp) {
        ipInput.value = savedIp;
    }
});

ipSaveBtn.addEventListener('click', function() {
    const ip = ipInput.value.trim();
    if (/^\d{1,3}(\.\d{1,3}){3}$/.test(ip)) {
        // Enregistrer localement
        localStorage.setItem('raspberry_ip', ip);
        // Envoyer au serveur Flask
        fetch('/api/set_pico_ip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ip })
        })
        .then(res => res.json())
        .then(data => {
            ipStatus.textContent = data.status === 'ok' ? 'IP enregistrée !' : 'Erreur: ' + data.message;
            ipStatus.style.color = data.status === 'ok' ? '#2ecc71' : '#e74c3c';
        })
        .catch(() => {
            ipStatus.textContent = 'Erreur réseau';
            ipStatus.style.color = '#e74c3c';
        });
    } else {
        ipStatus.textContent = 'Format IP invalide';
        ipStatus.style.color = '#e74c3c';
    }
});

function getPicoIp() {
    // Récupère l'IP de la Pico depuis le localStorage ou le champ
    return localStorage.getItem('raspberry_ip') || document.getElementById('ip-input').value.trim();
}

function updateObstacleDistance() {
    const picoIp = getPicoIp();
    if (!picoIp) {
        const el = document.getElementById('obstacle-distance-front');
        if (el) el.textContent = '--';
        return;
    }
    fetch(`http://${picoIp}:80/api/distance_obstacle/`)
        .then(res => res.json())
        .then(data => {
            let dist = data.distance;
            const el = document.getElementById('obstacle-distance-front');
            if (el) {
                if (dist !== undefined && dist !== null) {
                    dist = Math.round(dist * 10) / 10; // Arrondi à 0.1 près
                    el.textContent = dist + ' cm';
                } else {
                    el.textContent = '--';
                }
            }
        })
        .catch(() => {
            const el = document.getElementById('obstacle-distance-front');
            if (el) el.textContent = '??';
        });
}

// Fonction pour mettre à jour la détection de métal
function updateMetalDetection() {
    const picoIp = getPicoIp();
    const el = document.getElementById('metal-detect-value');
    const metalDiv = document.getElementById('metal-detect');
    let metalAudio = document.getElementById('metal-audio');
    
    if (!picoIp) {
        if (el) el.textContent = '--';
        if (metalDiv) metalDiv.classList.remove('metal-detected', 'metal-alert');
        if (metalAudio && !metalAudio.paused) {
            metalAudio.pause();
            isAudioPlaying = false;
        }
        return;
    }
    
    fetch(`http://${picoIp}:80/api/metal/`)
        .then(res => res.json())
        .then(data => {
            if (el && metalDiv) {
                if (data.metal === "metal") {
                    el.textContent = "Métal détecté";
                    metalDiv.classList.add('metal-detected', 'metal-alert');
                    
                    // Ne jouer l'audio que si il n'est pas déjà en cours
                    if (!isAudioPlaying) {
                        if (!metalAudio) {
                            metalAudio = new Audio('scary-movie-wazzup.mp3');
                            metalAudio.id = 'metal-audio';
                            document.body.appendChild(metalAudio);
                            
                            // Écouter la fin de l'audio
                            metalAudio.addEventListener('ended', function() {
                                isAudioPlaying = false;
                            });
                        }
                        
                        metalAudio.currentTime = 0;
                        metalAudio.play().then(() => {
                            isAudioPlaying = true;
                        }).catch(error => {
                            console.log('Erreur lecture audio:', error);
                            isAudioPlaying = false;
                        });
                    }
                } else {
                    el.textContent = "Aucun métal";
                    metalDiv.classList.remove('metal-detected', 'metal-alert');
                    if (metalAudio && !metalAudio.paused) {
                        metalAudio.pause();
                        metalAudio.currentTime = 0;
                        isAudioPlaying = false;
                    }
                }
            }
        })
        .catch(() => {
            if (el) el.textContent = '??';
            if (metalDiv) metalDiv.classList.remove('metal-detected', 'metal-alert');
            if (metalAudio && !metalAudio.paused) {
                metalAudio.pause();
                isAudioPlaying = false;
            }
        });
}


setInterval(updateObstacleDistance, 1500);
setInterval(updateMetalDetection, 1000);
