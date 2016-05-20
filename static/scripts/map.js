//Defines the map widget by using MapBox API
var campus = L.map('map_widget').setView([34.545, 135.506], 16);
L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
  attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
  maxZoom: 18,
  minZoom: 15,
  id: 'henriojord.02b78bop',
  accessToken: 'pk.eyJ1IjoiaGVucmlvam9yZCIsImEiOiJjaW52cW54NnExNWxwdWlrandxc25reTR3In0.y3sKYC35D3MExcrcZWqHyA'
}).addTo(campus);

var popup = L.popup();
var markers = new Array();
var selected_waypoints = new Array();
var default_waypoints = new Array();
var sectors = new Array();

//Development tool for easily Lat and Long on click
/*function onMapClick(e){
    popup
        .setLatLng(e.latlng)
        .setContent(e.latlng.toString())
        .openOn(campus);
}
campus.on('click', onMapClick);
*/

//Creates Leaflet polygon from defined campus limits
var bounds = L.polygon(campus_limits, {color:'green'}).addTo(campus);
campus.fitBounds(campus_limits);

function onBoundsClick(e){
  selected_waypoints.push([e.latlng["lat"], e.latlng["lng"]]);
  var marker = L.marker(e.latlng).addTo(campus);
  markers.push(marker);
}

bounds.on('click', function(e){onBoundsClick(e)});

//Creates Leaflet polygons objects from defined non admissible zones
function onObstacleClick(e){

}

for(var i = 0; i < non_admissible_zones.length; i++){
  obstacle = L.polygon(non_admissible_zones[i], {color: 'red'}).addTo(campus);
  obstacle.on('click', function(e){onObstacleClick(e)});
}


//Creates Leaflet polygons objects from defined sectors
for(var i = 0; i < sectors_bounds.length; i++){
  sector = L.polygon(sectors_bounds[i], {color: 'blue'});
  sectors.push(sector);
}

//Creates Leaflet circles objects from defined default waypoints
for (var i = 0; i < default_targets.length; i++){
  var waypoint = L.circleMarker(default_targets[i], {radius: 3, color: 'black'}).addTo(campus);
  default_waypoints.push(waypoint)
}
