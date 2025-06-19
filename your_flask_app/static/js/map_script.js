const map = L.map('map').setView([-15, -65], 3.5);

// Mapa base minimalista
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19
}).addTo(map);

// Gradiente azul bonito
function getColor(d) {
    return d > 250 ? '#08306b' :
           d > 200 ? '#08519c' :
           d > 150 ? '#2171b5' :
           d > 100 ? '#4292c6' :
           d > 50  ? '#6baed6' :
           d > 0   ? '#c6dbef' :
                     '#f7fbff';
}

// Estilo para cada país
function style(feature) {
    return {
        fillColor: getColor(feature.properties.count || 0),
        weight: 1.2,
        color: '#000',
        fillOpacity: 0.8
    };
}

// Cargar datos y pintar el mapa
async function loadDataAndMap() {
    try {
        const [dataRes, geoRes] = await Promise.all([
            fetch('/admin/api/data_mapa'),
            fetch('/static/data/latam_countries.geojson')
        ]);

        const studentCounts = await dataRes.json();
        const geojsonData = await geoRes.json();

        geojsonData.features.forEach(f => {
            const name = f.properties.name;
            f.properties.count = studentCounts[name] || 0;
        });

        const geoLayer = L.geoJson(geojsonData, {
            style: style,
            onEachFeature: (feature, layer) => {
                layer.bindPopup(`<b>${feature.properties.name}</b><br>Estudiantes: ${feature.properties.count}`);
                layer.on({
                    mouseover: e => {
                        e.target.setStyle({ weight: 3, color: '#333', fillOpacity: 1 });
                        e.target.bringToFront();
                    },
                    mouseout: e => geoLayer.resetStyle(e.target)
                });
            }
        }).addTo(map);

        map.fitBounds(geoLayer.getBounds());

    } catch (err) {
        console.error(err);
        alert("No se pudo cargar el mapa correctamente.");
    }
}

loadDataAndMap();
