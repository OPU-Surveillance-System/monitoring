/*
Draws the map element on master's GUI.
*/

//Defines the map widget by using MapBox API
var campus = L.map('map_widget').setView([34.545, 135.506], 16);
L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
  attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
  maxZoom: 25,
  minZoom: 15,
  id: 'henriojord.02b78bop',
  accessToken: 'pk.eyJ1IjoiaGVucmlvam9yZCIsImEiOiJjaW52cW54NnExNWxwdWlrandxc25reTR3In0.y3sKYC35D3MExcrcZWqHyA'
}, 1).addTo(campus);

var popup = L.popup();
var markers = new Array();
var selected_waypoints = new Array();
var default_waypoints = new Array();
var projection = new Array();
var sectors = new Array();
var plan = new Array();
var nb_patrol = 0;
var patrol_lengths = new Array();

//Development tool for easily Lat and Long on click
// function onMapClick(e){
//     popup
//         .setLatLng(e.latlng)
//         .setContent(e.latlng.toString())
//         //.setContent("lat: " + e.latlng.lat + ", long: " + e.latlng.lng)
//         .openOn(campus);
// }
// campus.on('click', onMapClick);

//Creates Leaflet polygon from defined campus limits
var bounds = L.polygon(campus_limits, {color:'green'}, 1).addTo(campus);
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
  obstacle = L.polygon(non_admissible_zones[i], {color: 'red'}, 1).addTo(campus);
  obstacle.on('click', function(e){onObstacleClick(e)});
}

//Creates Leaflet polygons objects from defined sectors
for(var i = 0; i < sectors_bounds.length; i++){
  sector = L.polygon(sectors_bounds[i], {color: 'blue'});
  sectors.push(sector);
}

//Creates Leaflet circles objects from defined default waypoints
for(var i = 0; i < default_targets.length; i++){
  var waypoint = L.circleMarker(default_targets[i], {radius: 3, color: 'grey'}, 1).addTo(campus);
  default_waypoints.push(waypoint);
}

//Add starting point
var starting_point = [
  [34.54541567027274, 135.50398817296576],
  [34.545408860722944, 135.5039954066508],
  [34.545402051172715, 135.5040026403347],
  [34.54539524162206, 135.5040098740174],
  [34.54538843207099, 135.50401710769893],
  [34.54538162251949, 135.50402434137928],
  [34.54537481296756, 135.50403157505846],
  [34.54536800341522, 135.50403880873645],
  [34.54536119386244, 135.50404604241328],
];

for(var i = 0; i < starting_point.length; i++){
  starting_point_marker = L.circleMarker(starting_point[i], {radius: 4, color: 'black'}, 1).addTo(campus);
}

//Creates Leaflet polygone objects from defined project non admissible zones
var p_b = L.polygon(projected_bounds, {color: 'blue'}).addTo(campus);
projection.push(p_b);
for (var i = 0; i < projected_non_admissible_zones.length; i++){
  var obstacle = L.polygon(projected_non_admissible_zones[i], {color: 'red'}, 1).addTo(campus);
  projection.push(obstacle);
}
