let map;
let createdZone;

// Initialiser la carte
function initMap() {
    map = L.map('map').setView([48.8566, 2.3522], 13); // Coordonnées par défaut (Paris)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    }).addTo(map);

    // Ajouter un exemple de zone
    createdZone = L.rectangle([[48.856, 2.351], [48.857, 2.353]], {
        color: "#ff7800",
        weight: 1
    }).addTo(map);
}

// Réinitialiser la zone
function resetZone() {
    if (createdZone) {
        map.removeLayer(createdZone);
        createdZone = null;
        console.log("Zone supprimée.");
    }
}

// Ajouter un écouteur pour le bouton "Reset Zone"
document.getElementById('reset-zone-btn').addEventListener('click', resetZone);

// Initialiser la carte au chargement de la page
document.addEventListener('DOMContentLoaded', initMap);
