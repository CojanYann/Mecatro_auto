// This file contains the JavaScript code for the application. It handles the interactive features, such as updating the user interface, managing WebSocket connections, and simulating sensor data.

const servoSlider = document.getElementById('servo-slider');
const servoValue = document.getElementById('servo-value');
const sensor1Value = document.getElementById('sensor1-value');
const sensor1Status = document.getElementById('sensor1-status');
const sensor2Value = document.getElementById('sensor2-value');
const sensor2Status = document.getElementById('sensor2-status');
const compassDegrees = document.getElementById('compass-degrees');
const gpsLatitude = document.getElementById('gps-latitude');
const gpsLongitude = document.getElementById('gps-longitude');
const activityLog = document.getElementById('activity-log');
const connectionStatus = document.getElementById('connection-status');
const ipInput = document.getElementById('ip-input');
const connectButton = document.getElementById('connect-button');
const reconnectButton = document.getElementById('reconnect-button');
const getDataButton = document.getElementById('get-data-button');
const getDistancesButton = document.getElementById('get-distances-button');
const batteryLevel = document.getElementById('battery-level');
const batteryText = document.getElementById('battery-text');
const powerToggle = document.getElementById('power-toggle');
const modeBtn = document.getElementById('mode-btn');
let isAutoMode = false;
modeBtn.addEventListener('click', function() {
    isAutoMode = !isAutoMode;
    if (isAutoMode) {
        modeBtn.textContent = "Auto";
        modeBtn.classList.add('active');
        sendToRobot("mode_auto");
        addLogEntry("Mode automatique activé");
    } else {
        modeBtn.textContent = "Manuel";
        modeBtn.classList.remove('active');
        sendToRobot("mode_manuel");
        addLogEntry("Mode manuel activé");
    }
});

let servoPosition = 90;
let sensor1Distance = 0;
let sensor2Distance = 0;
let heading = 0;
let gpsCoords = {
    latitude: 48.8566,
    longitude: 2.3522
};
let map;
let robotMarker;
let ws;
let isSimulating = true;
let reconnectTimer = null;

function connectWebSocket() {
    const ipAddress = ipInput.value.trim();
    const wsUrl = `ws://${ipAddress}:8765`;

    if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
    }

    try {
        if (ws) {
            ws.close();
        }

        addLogEntry("Tentative de connexion à " + wsUrl);
        connectionStatus.className = "connection-status";
        connectionStatus.title = "Connexion en cours...";

        ws = new WebSocket(wsUrl);

        ws.onopen = function() {
            addLogEntry("Connexion WebSocket établie avec succès");
            connectionStatus.className = "connection-status connected";
            connectionStatus.title = "Connecté";
            isSimulating = false;
            sendToRobot("getdistances");
        };

        ws.onmessage = function(event) {
            try {
                const rawData = event.data;
                const data = JSON.parse(rawData);
                processIncomingData(data);
            } catch (error) {
                processTextData(event.data);
            }
        };

        ws.onclose = function(event) {
            isSimulating = true;
            reconnectTimer = setTimeout(connectWebSocket, 5000);
        };

        ws.onerror = function(error) {
            isSimulating = true;
        };
    } catch (error) {
        isSimulating = true;
        reconnectTimer = setTimeout(connectWebSocket, 5000);
    }
}

function processTextData(text) {
    const distance1Match = text.match(/Distance\s*1\s*:\s*(\d+\.?\d*)\s*cm/i);
    const distance2Match = text.match(/Distance\s*2\s*:\s*(\d+\.?\d*)\s*cm/i);

    if (distance1Match && distance1Match[1]) {
        updateSensor1(parseFloat(distance1Match[1]));
    }

    if (distance2Match && distance2Match[1]) {
        updateSensor2(parseFloat(distance2Match[1]));
    }
}

function processIncomingData(data) {
    if (data.type === "distance_update" && data.distances) {
        if (data.distances.sensor1 !== undefined) {
            updateSensor1(parseFloat(data.distances.sensor1));
        }
        if (data.distances.sensor2 !== undefined) {
            updateSensor2(parseFloat(data.distances.sensor2));
        }
    } else if (data.type === "full_update" || data.type === "initial_data" || data.type === "data_request") {
        if (data.distances) {
            if (data.distances.sensor1 !== undefined) {
                updateSensor1(parseFloat(data.distances.sensor1));
            }
            if (data.distances.sensor2 !== undefined) {
                updateSensor2(parseFloat(data.distances.sensor2));
            }
        }

        if (data.compass && data.compass.heading !== undefined) {
            updateCompass(parseFloat(data.compass.heading));
        }

        if (data.location) {
            if (data.location.latitude !== undefined && data.location.longitude !== undefined) {
                updateGPSCoordinates(
                    parseFloat(data.location.latitude),
                    parseFloat(data.location.longitude)
                );
            }
        }
    }
}

function sendToRobot(command, value) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        const data = value !== undefined ? JSON.stringify({ command, value }) : command;
        ws.send(data);
        return true;
    } else {
        return false;
    }
}

function initMap() {
    map = L.map('map').setView([gpsCoords.latitude, gpsCoords.longitude], 18);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    }).addTo(map);

    const robotIcon = L.divIcon({
        className: 'robot-marker-icon',
        html: '<div style="background-color: #eb0503; width: 16px; height: 16px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 8px rgba(0,0,0,0.5);"></div>',
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    });

    robotMarker = L.marker([gpsCoords.latitude, gpsCoords.longitude], { icon: robotIcon }).addTo(map);
}

function updateGPSCoordinates(lat, lng) {
    gpsCoords.latitude = lat;
    gpsCoords.longitude = lng;

    const latDirection = lat >= 0 ? "N" : "S";
    const lngDirection = lng >= 0 ? "E" : "W";

    gpsLatitude.textContent = `${Math.abs(lat).toFixed(6)}° ${latDirection}`;
    gpsLongitude.textContent = `${Math.abs(lng).toFixed(6)}° ${lngDirection}`;

    if (robotMarker && map) {
        robotMarker.setLatLng([lat, lng]);
        map.setView([lat, lng]);
    }
}

function updateCompass(degrees) {
    heading = degrees;
    compassDegrees.textContent = `${Math.round(degrees)}°`;
}

function updateServo(position) {
    servoPosition = position;
    servoValue.textContent = `Position: ${position}°`;
    servoSlider.value = position;
}

function updateSensor1(distance) {
    sensor1Distance = distance;
    sensor1Value.textContent = distance.toFixed(1);
    
    // Mise à jour du statut en fonction de la distance
    if (distance < 10) {
        sensor1Status.className = "sensor-status danger";
        sensor1Status.textContent = "Obstacle proche";
    } else if (distance < 30) {
        sensor1Status.className = "sensor-status warning";
        sensor1Status.textContent = "Attention";
    } else {
        sensor1Status.className = "sensor-status safe";
        sensor1Status.textContent = "Distance sûre";
    }
}

function updateSensor2(distance) {
    sensor2Distance = distance;
    sensor2Value.textContent = distance.toFixed(1);
    
    // Mise à jour du statut en fonction de la distance
    if (distance < 10) {
        sensor2Status.className = "sensor-status danger";
        sensor2Status.textContent = "Obstacle proche";
    } else if (distance < 30) {
        sensor2Status.className = "sensor-status warning";
        sensor2Status.textContent = "Attention";
    } else {
        sensor2Status.className = "sensor-status safe";
        sensor2Status.textContent = "Distance sûre";
    }
}

// Affichage du niveau de batterie (valeur simulée ou à connecter à vos données réelles)
function updateBatteryIndicator(percent) {
    // Clamp entre 0 et 100
    percent = Math.max(0, Math.min(100, percent));
    batteryLevel.style.width = percent + "%";
    batteryText.textContent = percent + "%";
    // Couleur dynamique selon le niveau
    if (percent > 50) {
        batteryLevel.style.background = "#2ecc71";
    } else if (percent > 20) {
        batteryLevel.style.background = "#f39c12";
    } else {
        batteryLevel.style.background = "#e74c3c";
    }
}

// Exemple d'appel (à remplacer par vos données réelles)
updateBatteryIndicator(75);

function addLogEntry(message) {
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    const now = new Date();
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
    entry.innerHTML = `<span class="log-time">${timeStr}</span><span class="log-message">${message}</span>`;
    activityLog.prepend(entry);
}

// Ajout d'une fonction pour réinitialiser tous les indicateurs
function resetAllIndicators() {
    // Réinitialiser le servomoteur
    updateServo(90);
    
    // Réinitialiser les capteurs à ultrason
    updateSensor1(0);
    updateSensor2(0);
    
    // Mettre à jour les statuts des capteurs
    sensor1Status.className = "sensor-status safe";
    sensor1Status.textContent = "Distance sûre";
    sensor2Status.className = "sensor-status safe";
    sensor2Status.textContent = "Distance sûre";
    
    // Réinitialiser la boussole
    updateCompass(0);
    
    // Réinitialiser les coordonnées GPS à une valeur par défaut
    updateGPSCoordinates(48.8566, 2.3522);
    
    // Ajouter une entrée dans le journal
    addLogEntry("Tous les indicateurs ont été réinitialisés");
}

servoSlider.addEventListener('input', function() {
    const position = parseInt(this.value);
    updateServo(position);
    sendToRobot(position.toString());
});

connectButton.addEventListener('click', function() {
    connectWebSocket();
});

reconnectButton.addEventListener('click', function() {
    connectWebSocket();
});

getDataButton.addEventListener('click', function() {
    sendToRobot("getdata");
});

getDistancesButton.addEventListener('click', function() {
    sendToRobot("getdistances");
});

document.addEventListener('DOMContentLoaded', function() {
    initMap();
    resetAllIndicators(); // Utiliser la nouvelle fonction au chargement
    connectWebSocket();

    // Variables pour le contrôle du servomoteur
    const servoLeftButton = document.getElementById('servo-left');
    const servoRightButton = document.getElementById('servo-right');
    const servoValueDisplay = document.getElementById('servo-value');
    let servoPosition = 90; // Position initiale
    const servoStep = 10; // Pas de changement à chaque clic
    
    // Gestion des boutons directionnels
    servoLeftButton.addEventListener('click', function() {
        if (servoPosition > 0) {
            servoPosition -= servoStep;
            updateServoPosition();
        }
    });
    
    servoRightButton.addEventListener('click', function() {
        if (servoPosition < 180) {
            servoPosition += servoStep;
            updateServoPosition();
        }
    });
    
    // Fonction pour mettre à jour l'affichage et envoyer la position au serveur
    function updateServoPosition() {
        servoValueDisplay.textContent = `Position: ${servoPosition}°`;
        
        // Si une connexion WebSocket existe, envoyez la position au serveur
        if (window.socket && window.socket.readyState === WebSocket.OPEN) {
            window.socket.send(JSON.stringify({
                type: 'servo',
                position: servoPosition
            }));
        }
    }

    // Récupération des éléments de contrôle
    const speedSlider = document.getElementById('speed-slider');
    const speedValue = document.getElementById('speed-value');
    const forwardBtn = document.getElementById('forward-btn');
    const backwardBtn = document.getElementById('backward-btn');
    const leftBtn = document.getElementById('left-btn');
    const rightBtn = document.getElementById('right-btn');
    const stopBtn = document.getElementById('stop-btn');
    
    // Configuration du slider de vitesse
    speedSlider.addEventListener('input', function() {
        // Calcul du pourcentage réel selon la position du slider (min/max)
        const min = parseInt(speedSlider.min, 10);
        const max = parseInt(speedSlider.max, 10);
        const val = parseInt(speedSlider.value, 10);
        const percent = Math.round(((val - min) / (max - min)) * 100);
        speedValue.textContent = `Vitesse : ${percent}%`;
    });

    // Initialiser l'affichage de la vitesse au chargement
    (function() {
        const min = parseInt(speedSlider.min, 10);
        const max = parseInt(speedSlider.max, 10);
        const val = parseInt(speedSlider.value, 10);
        const percent = Math.round(((val - min) / (max - min)) * 100);
        speedValue.textContent = `Vitesse : ${percent}%`;
    })();
    
    // Fonction pour envoyer une commande au robot
    function sendCommand(command, value = null) {
        if (ws && ws.readyState === WebSocket.OPEN) {
            const data = {
                type: 'move',
                command: command
            };
            
            if (value !== null) {
                data.value = value;
            }
            
            ws.send(JSON.stringify(data));
            addLogEntry(`Commande envoyée: ${command}${value !== null ? ' (' + value + '%)' : ''}`);
        } else {
            console.warn('Pas de connexion WebSocket disponible');
        }
    }
    
    // Configuration des boutons directionnels
    forwardBtn.addEventListener('click', () => sendCommand('forward', speedSlider.value));
    backwardBtn.addEventListener('click', () => sendCommand('backward', speedSlider.value));
    leftBtn.addEventListener('click', () => sendCommand('left', speedSlider.value));
    rightBtn.addEventListener('click', () => sendCommand('right', speedSlider.value));
    stopBtn.addEventListener('click', () => sendCommand('stop'));
    
    // Support des touches clavier
    document.addEventListener('keydown', function(e) {
        switch(e.key) {
            case 'ArrowUp':
                forwardBtn.click();
                break;
            case 'ArrowDown':
                backwardBtn.click();
                break;
            case 'ArrowLeft':
                leftBtn.click();
                break;
            case 'ArrowRight':
                rightBtn.click();
                break;
            case ' ': // Espace
                stopBtn.click();
                break;
        }
    });
});

// Gestion du bouton ON/OFF pour allumer/éteindre le robot
let isPowerOn = true;
powerToggle.addEventListener('click', function() {
    isPowerOn = !isPowerOn;
    if (isPowerOn) {
        powerToggle.textContent = "ON";
        powerToggle.classList.remove('off');
        sendToRobot("power_on");
        addLogEntry("Robot allumé");
    } else {
        powerToggle.textContent = "OFF";
        powerToggle.classList.add('off');
        sendToRobot("power_off");
        addLogEntry("Robot éteint");
    }
});