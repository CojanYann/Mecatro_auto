let map;
let createdZone;
let drawingMode = false;
let drawnPoints = [];
let currentPolygon = null;

// Initialiser la carte
function initMap() {
    map = L.map('map').setView([48.8566, 2.3522], 13); // Coordonnées par défaut (Paris)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    }).addTo(map);

    // Créer les boutons de contrôle de dessin
    createDrawingControls();
    
    // Ajouter un exemple de zone
    createdZone = L.rectangle([[48.856, 2.351], [48.857, 2.353]], {
        color: "#ff7800",
        weight: 1
    }).addTo(map);
    
    // Ajouter l'écouteur d'événement pour le clic sur la carte
    map.on('click', onMapClick);
}

// Fonction appelée lors du clic sur la carte
function onMapClick(e) {
    if (!drawingMode) return;
    
    const latlng = e.latlng;
    drawnPoints.push([latlng.lat, latlng.lng]);
    
    // Marquer le point cliqué
    L.circleMarker(latlng, {
        color: '#3388ff',
        radius: 5
    }).addTo(map);
    
    // Mettre à jour le polygone en cours de dessin
    updateCurrentPolygon();
}

// Mettre à jour le polygone en cours de dessin
function updateCurrentPolygon() {
    if (currentPolygon) {
        map.removeLayer(currentPolygon);
    }
    
    if (drawnPoints.length >= 2) {
        currentPolygon = L.polyline(drawnPoints, {
            color: 'blue',
            weight: 2
        }).addTo(map);
    }
    
    // Si nous avons au moins 3 points, on peut dessiner un polygone
    if (drawnPoints.length >= 3) {
        if (currentPolygon) {
            map.removeLayer(currentPolygon);
        }
        currentPolygon = L.polygon(drawnPoints, {
            color: 'blue',
            fillColor: '#3388ff',
            fillOpacity: 0.3
        }).addTo(map);
    }
}

// Créer les boutons de contrôle de dessin
function createDrawingControls() {
    const drawControl = document.createElement('div');
    drawControl.className = 'map-controls';
    drawControl.innerHTML = `
        <button id="draw-zone-btn" class="map-button">Dessiner une zone</button>
        <button id="finish-zone-btn" class="map-button" style="display:none;">Terminer</button>
        <button id="cancel-zone-btn" class="map-button" style="display:none;">Annuler</button>
    `;
    document.querySelector('#map-container').appendChild(drawControl);
    
    // Ajouter les écouteurs d'événements pour les nouveaux boutons
    document.getElementById('draw-zone-btn').addEventListener('click', startDrawing);
    document.getElementById('finish-zone-btn').addEventListener('click', finishDrawing);
    document.getElementById('cancel-zone-btn').addEventListener('click', cancelDrawing);
}

// Démarrer le dessin
function startDrawing() {
    drawingMode = true;
    drawnPoints = [];
    
    // Afficher/masquer les boutons appropriés
    document.getElementById('draw-zone-btn').style.display = 'none';
    document.getElementById('finish-zone-btn').style.display = 'inline-block';
    document.getElementById('cancel-zone-btn').style.display = 'inline-block';
    document.getElementById('reset-zone-btn').style.display = 'none';
    
    // Changer le curseur pour indiquer le mode dessin
    map._container.style.cursor = 'crosshair';
}

// Terminer le dessin
function finishDrawing() {
    if (drawnPoints.length < 3) {
        alert("Il faut au moins 3 points pour créer une zone.");
        return;
    }
    
    drawingMode = false;
    
    // Supprimer l'ancienne zone si elle existe
    if (createdZone) {
        map.removeLayer(createdZone);
    }
    
    // Créer la zone finale à partir des points dessinés
    createdZone = L.polygon(drawnPoints, {
        color: "#ff7800",
        fillColor: '#ff7800',
        fillOpacity: 0.5,
        weight: 2
    }).addTo(map);
    
    // Supprimer le polygone temporaire
    if (currentPolygon) {
        map.removeLayer(currentPolygon);
        currentPolygon = null;
    }
    
    // Réinitialiser l'interface
    document.getElementById('draw-zone-btn').style.display = 'inline-block';
    document.getElementById('finish-zone-btn').style.display = 'none';
    document.getElementById('cancel-zone-btn').style.display = 'none';
    document.getElementById('reset-zone-btn').style.display = 'inline-block';
    
    // Réinitialiser le curseur
    map._container.style.cursor = '';
    
    console.log("Zone créée avec " + drawnPoints.length + " points");
}

// Annuler le dessin
function cancelDrawing() {
    drawingMode = false;
    drawnPoints = [];
    
    // Supprimer le polygone temporaire
    if (currentPolygon) {
        map.removeLayer(currentPolygon);
        currentPolygon = null;
    }
    
    // Réinitialiser l'interface
    document.getElementById('draw-zone-btn').style.display = 'inline-block';
    document.getElementById('finish-zone-btn').style.display = 'none';
    document.getElementById('cancel-zone-btn').style.display = 'none';
    document.getElementById('reset-zone-btn').style.display = 'inline-block';
    
    // Réinitialiser le curseur
    map._container.style.cursor = '';
    
    // Supprimer tous les marqueurs de points
    map.eachLayer(function(layer) {
        if (layer instanceof L.CircleMarker) {
            map.removeLayer(layer);
        }
    });
}

// Réinitialiser la zone
function resetZone() {
    if (createdZone) {
        map.removeLayer(createdZone);
        createdZone = null;
        console.log("Zone supprimée.");
        
        // Supprimer tous les marqueurs de points
        map.eachLayer(function(layer) {
            if (layer instanceof L.CircleMarker) {
                map.removeLayer(layer);
            }
        });
    }
}

// Ajouter un écouteur pour le bouton "Reset Zone"
document.getElementById('reset-zone-btn').addEventListener('click', resetZone);

// Initialiser la carte au chargement de la page
document.addEventListener('DOMContentLoaded', initMap);
