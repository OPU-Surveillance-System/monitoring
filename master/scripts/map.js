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

/*var campus_limit = L.polygon([
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
]).addTo(campus);*/

var zone_iwing = L.polygon([
  [34.54669, 135.50147],
  [34.54624, 135.50142],
  [34.54596, 135.50169],
  [34.54667, 135.5027],
  [34.54715, 135.50214]
]).addTo(campus);
zone_iwing.bindPopup("I-wing sector");

var zone_B6 = L.polygon([
  [34.54632, 135.50228],
  [34.54555, 135.50329],
  [34.54582, 135.50365],
  [34.54662, 135.50272]
]).addTo(campus);
zone_B6.bindPopup("B6 sector");

var zone_B10 = L.polygon([
  [34.5463, 135.50227],
  [34.54593, 135.50173],
  [34.5451, 135.5026],
  [34.54551, 135.50325]
]).addTo(campus);
zone_B10.bindPopup("B10 sector");

var zone_B4 = L.polygon([
  [34.54578, 135.5037],
  [34.54505, 135.50268],
  [34.54396, 135.50382],
  [34.54482, 135.50481]
]).addTo(campus);
zone_B4.bindPopup("B4 sector");

var zone_B11 = L.polygon([
  [34.54738, 135.50394],
  [34.54792, 135.50318],
  [34.54719, 135.5022],
  [34.54653, 135.50296]
]).addTo(campus);
zone_B11.bindPopup("B11 sector");

var zone_pond = L.polygon([
  [34.5485, 135.50398],
  [34.54793, 135.50324],
  [34.54737, 135.504],
  [34.54704, 135.50363],
  [34.54627, 135.50452],
  [34.54708, 135.50565]
]).addTo(campus);
zone_pond.bindPopup("pond sector");

var zone_B5 = L.polygon([
  [34.54698, 135.50356],
  [34.5465, 135.503],
  [34.54581, 135.50377],
  [34.54631, 135.50436]
]).addTo(campus);
zone_B5.bindPopup("B5 sector");

var zone_infirmary = L.polygon([
  [34.54626, 135.50442],
  [34.54579, 135.50382],
  [34.54542, 135.50422],
  [34.5459, 135.50484]
]).addTo(campus);
zone_infirmary.bindPopup("infirmary sector");

var zone_refectory = L.polygon([
  [34.54622, 135.50456],
  [34.54705, 135.50568],
  [34.5468, 135.50597],
  [34.54593, 135.50489]
]).addTo(campus);
zone_refectory.bindPopup("refectory sector");

var zone_B3 = L.polygon([
  [34.54578, 135.50478],
  [34.54538, 135.50428],
  [34.54485, 135.50488],
  [34.54525, 135.50539]
]).addTo(campus);
zone_B3.bindPopup("B3 sector");

var zone_B1 = L.polygon([
  [34.54676, 135.50601],
  [34.54582, 135.50484],
  [34.54528, 135.50543],
  [34.54623, 135.50665]
]).addTo(campus);
zone_B1.bindPopup("B1 sector");

var zone_library = L.polygon([
  [34.54468, 135.50665],
  [34.54542, 135.50571],
  [34.54481, 135.50492],
  [34.54393, 135.50586]
]).addTo(campus);
zone_library.bindPopup("library sector");

var zone_A5 = L.polygon([
  [34.54835, 135.50617],
  [34.5476, 135.50516],
  [34.54706, 135.50575],
  [34.54786, 135.50673]
]).addTo(campus);
zone_A5.bindPopup("A5 sector");

var zone_A9 = L.polygon([
  [34.54929, 135.50501],
  [34.54837, 135.50612],
  [34.54763, 135.50512],
  [34.54852, 135.50404]
]).addTo(campus);
zone_A9.bindPopup("A9 sector");

var zone_A3 = L.polygon([
  [34.54781, 135.50678],
  [34.54704, 135.50579],
  [34.54626, 135.50668],
  [34.54705, 135.50768]
]).addTo(campus);
zone_A3.bindPopup("A3 sector");

var zone_stadium = L.polygon([
  [34.54747, 135.50902],
  [34.54551, 135.50652],
  [34.5444, 135.5078],
  [34.54422, 135.50784],
  [34.545, 135.5107],
  [34.54658, 135.50977],
  [34.54719, 135.50936]
]).addTo(campus);
zone_stadium.bindPopup("stadium sector");

var zone_shirasagimonAvenue = L.polygon([
  [34.54778, 135.50871],
  [34.54545, 135.50572],
  [34.54523, 135.50601],
  [34.54753, 135.50898]
]).addTo(campus);
zone_shirasagimonAvenue.bindPopup("Shirasagimon Avenue sector");

var zone_garden = L.polygon([
  [34.54476, 135.50488],
  [34.54394, 135.50387],
  [34.54124, 135.50665],
  [34.54217, 135.50765]
]).addTo(campus);
zone_garden.bindPopup("garden sector");

var zone_racecourse = L.polygon([
  [34.54266, 135.50983],
  [34.5432, 135.50899],
  [34.54189, 135.50752],
  [34.5413, 135.50813]
]).addTo(campus);
zone_racecourse.bindPopup("racecourse sector");

var zone_C17 = L.polygon([
  [34.54548, 135.50642],
  [34.54521, 135.5061],
  [34.54468, 135.50672],
  [34.54388, 135.50592],
  [34.54343, 135.50642],
  [34.5438, 135.50695],
  [34.54405, 135.5074],
  [34.54419, 135.50778],
  [34.54438, 135.50773]
]).addTo(campus);
zone_C17.bindPopup("C17 sector");

var zone_C10 = L.polygon([
  [34.54339, 135.50648],
  [34.54219, 135.50774],
  [34.54324, 135.50899],
  [34.5427, 135.50987],
  [34.54354, 135.51097],
  [34.54366, 135.51097],
  [34.54375, 135.51149],
  [34.54496, 135.51074],
  [34.54418, 135.50784],
  [34.54401, 135.50744]
]).addTo(campus);
zone_C10.bindPopup("C10 sector");

var zone_A12 = L.polygon([
  [34.5501, 135.50607],
  [34.5493, 135.50504],
  [34.54709, 135.50773],
  [34.54784, 135.50865]
]).addTo(campus);
zone_A12.bindPopup("A12 sector");
