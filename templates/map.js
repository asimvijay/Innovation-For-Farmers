function show() {
    document.getElementById('').classList.toggle('active');
}





var map = L.map('map').setView([30.3753, 69.3451], 5);

var osm = L.tileLayer('https://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}', {

    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
})
osm.addTo(map);

var marker = L.marker([30.3753, 69.3451]).addTo(map);





var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);
// Initialise the draw control and pass it the FeatureGroup of editable layers
self = this;
self.drawControl = new L.Control.Draw({
    draw: true,
    edit: {
        featureGroup: drawnItems
    }
});

map.on('drawnItems', function (e) {
    var type = e.layerType;
    var layer = e.layer;
    console.log(e)
    drawnItems.addLayer(layer);
});



map.addControl(drawControl);
hide_draw_ctrls();

//add leaflet search option with osm
var option = {
    position: 'topleft', // topright, topleft, bottomright, bottomleft

}

var sidebar = L.control.sidebar('sidebar', {
    position: 'left'
});

map.addControl(sidebar);





$('#search-btn').click(function () {
    var latlng = $("#search").val();
    var latlngArr = latlng.split(",");
    var lat = latlngArr[0];
    var lng = latlngArr[1];
    map.setView([lat, lng], 8);
    marker.setLatlng([lat, lng]);

});
