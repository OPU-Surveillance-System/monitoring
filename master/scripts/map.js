var campus = L.map('map_widget').setView([34.545, 135.506], 16);
L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
  attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
  maxZoom: 18,
  minZoom: 15,
  id: 'henriojord.02b78bop',
  accessToken: 'pk.eyJ1IjoiaGVucmlvam9yZCIsImEiOiJjaW52cW54NnExNWxwdWlrandxc25reTR3In0.y3sKYC35D3MExcrcZWqHyA'
}).addTo(campus);

var popup = L.popup();

function onMapClick(e) {
    popup
        .setLatLng(e.latlng)
        .setContent("You clicked the map at " + e.latlng.toString())
        .openOn(campus);
}

campus.on('click', onMapClick);

var campus_limit = L.polygon([
    [34.55011, 135.50607],
    [34.54669, 135.50147],
    [34.54624, 135.50142],
    [34.54125, 135.50665],
    [34.5419, 135.50744],
    [34.5413, 135.50814],
    [34.54354, 135.51096],
    [34.54365, 135.51098],
    [34.54376, 135.51148],
    [34.5472, 135.50935]
]).addTo(campus);
