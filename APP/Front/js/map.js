// Initialisation des fonds de carte
const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, // essaie 22 ou 23
    attribution: '© OpenStreetMap'
});

const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19, // essaie 22 ou 23
    attribution: 'Imagery © Esri'
});

// Initialisation de la carte
const map = L.map('map', {
    center: [47.62, -2.78], // Coordonnées par défaut (ex: Paris)
    zoom: 10,
    layers: [satelliteLayer],
});

// Contrôle pour changer de fond de carte
const baseMaps = {
    "Plan": osmLayer,
    "Satellite": satelliteLayer
};

L.control.layers(baseMaps).addTo(map);

// --- Ajout du dessin de zone ---
let drawing = false;
let points = [];
let markers = [];
let polyline = null;
let polygon = null;

// --- Marqueur du robot ---
let robotMarker = null;
let robotCentered = false; // Pour centrer la carte une seule fois

// Icône point rouge pour le robot
const robotIcon = L.divIcon({
    className: 'robot-point-icon',
    html: '<svg width="22" height="22" viewBox="0 0 22 22"><circle cx="11" cy="11" r="8" fill="#eb0503" stroke="#fff" stroke-width="3"/></svg>',
    iconSize: [22, 22],
    iconAnchor: [11, 11]
});

// Boutons
const drawBtn = document.getElementById('draw-zone-btn');
const finishBtn = document.getElementById('finish-zone-btn');
const cancelBtn = document.getElementById('cancel-zone-btn');
const deleteBtn = document.getElementById('delete-zone-btn');

// Fonction pour afficher ou mettre à jour la position du robot
function updateRobotPosition(lat, lng) {
    if (robotMarker) {
        robotMarker.setLatLng([lat, lng]);
        robotMarker.openPopup(); // Ouvre la popup à chaque mise à jour
    } else {
        robotMarker = L.marker([lat, lng], {icon: robotIcon, title: "Robot", zIndexOffset: 1000}).addTo(map);
        console.log("Marqueur robot ajouté à la carte:", lat, lng);
    }
    // Centrer la carte sur le robot la première fois
    if (!robotCentered) {
        map.setView([lat, lng], 17); // Zoom sur le robot 
        robotCentered = true;
    }
}

// Fonction pour récupérer la position du robot depuis l'API
function fetchRobotPosition() {
    fetch('/api/coordrobot/')
        .then(response => response.json())
        .then(data => {
            // Affiche les données reçues dans la console et dans la section log
            console.log("Coordonnées robot reçues:", data);
            const logDiv = document.getElementById('json-log');
            if (logDiv) {
                logDiv.textContent = JSON.stringify(data, null, 2);
            }
            // Vérifie que lat et lng sont bien des nombres valides
            if (
                data &&
                typeof data.lat === 'number' &&
                typeof data.lng === 'number' &&
                !isNaN(data.lat) &&
                !isNaN(data.lng)
            ) {
                updateRobotPosition(data.lat, data.lng);
            } else {
                // Si les coordonnées sont invalides, retire le marqueur
                if (robotMarker) {
                    map.removeLayer(robotMarker);
                    robotMarker = null;
                    robotCentered = false;
                }
            }
        })
        .catch(error => {
            console.error("Erreur lors de la récupération de la position du robot:", error);
        });
}

// Rafraîchir la position du robot toutes les 2 secondes
setInterval(fetchRobotPosition, 5000);
// Appel initial
fetchRobotPosition();

// Activer le mode dessin
drawBtn.addEventListener('click', function() {
    drawing = true;
    points = [];
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    if (polyline) { map.removeLayer(polyline); polyline = null; }
    if (polygon) { map.removeLayer(polygon); polygon = null; }
    finishBtn.style.display = '';
    cancelBtn.style.display = '';
    drawBtn.style.display = 'none';
});

// Ajouter un point sur la carte
map.on('click', function(e) {
    if (!drawing) return;
    const latlng = e.latlng;
    points.push([latlng.lat, latlng.lng]);
    const marker = L.marker(latlng).addTo(map);
    markers.push(marker);

    // Mettre à jour la ligne
    if (polyline) map.removeLayer(polyline);
    polyline = L.polyline(points, {color: 'blue'}).addTo(map);
});

// Terminer la zone
finishBtn.addEventListener('click', function() {
    if (points.length < 3) return; // Il faut au moins 3 points
    drawing = false;
    // Fermer le polygone
    if (polyline) { map.removeLayer(polyline); polyline = null; }
    if (polygon) map.removeLayer(polygon);
    polygon = L.polygon(points, {color: 'blue', fillColor: 'blue', fillOpacity: 0.3}).addTo(map);

    // Envoyer les coordonnées à l'API
    fetch('/api/coordgsp/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({coords: points})
    });

    finishBtn.style.display = 'none';
    cancelBtn.style.display = 'none';
    drawBtn.style.display = '';
});

// Annuler le dessin
cancelBtn.addEventListener('click', function() {
    drawing = false;
    points = [];
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    if (polyline) { map.removeLayer(polyline); polyline = null; }
    if (polygon) { map.removeLayer(polygon); polygon = null; }
    finishBtn.style.display = 'none';
    cancelBtn.style.display = 'none';
    drawBtn.style.display = '';
});

// Supprimer la zone dessinée
deleteBtn.addEventListener('click', function() {
    if (polygon) { map.removeLayer(polygon); polygon = null; }
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    points = [];
    if (polyline) { map.removeLayer(polyline); polyline = null; }
});

// Fonction pour afficher une zone à partir d'une liste de points
function displayZoneFromCoords(coords) {
    // Nettoyer l'affichage précédent
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    if (polyline) { map.removeLayer(polyline); polyline = null; }
    if (polygon) { map.removeLayer(polygon); polygon = null; }
    points = [];

    if (Array.isArray(coords) && coords.length > 0) {
        coords.forEach(pt => {
            const marker = L.marker(pt).addTo(map);
            markers.push(marker);
            points.push(pt);
        });
        polyline = L.polyline(points, {color: 'blue'}).addTo(map);
        if (points.length >= 3) {
            polygon = L.polygon(points, {color: 'blue', fillColor: 'blue', fillOpacity: 0.3}).addTo(map);
        }
        // Centrer la carte sur la zone avec un zoom maximum limité
        map.fitBounds(L.latLngBounds(points), { maxZoom: 19 });
    }
}

// Au chargement, récupérer et afficher la zone si elle existe
fetch('/api/coordgsp/')
    .then(response => response.json())
    .then(data => {
        if (data && Array.isArray(data.coords) && data.coords.length > 0) {
            displayZoneFromCoords(data.coords);
        }
    });
