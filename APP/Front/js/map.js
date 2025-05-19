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

// Boutons
const drawBtn = document.getElementById('draw-zone-btn');
const finishBtn = document.getElementById('finish-zone-btn');
const cancelBtn = document.getElementById('cancel-zone-btn');
const deleteBtn = document.getElementById('delete-zone-btn');

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
