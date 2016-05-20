//Asks Python for computing path
function computePath(){
  $.ajax({
    type: 'post',
    url: '/pathPlanner',
    data: JSON.stringify({
            nb_drones: $('#nb_drones_entry').val(),
            "starting_point": starting_point,
            "default_waypoints": default_targets,
            "selected_waypoints": selected_waypoints,
            "obstacles":non_admissible_zones}),
    //dataType:'json',
    contentType: "application/json; charset=utf-8",
    success: function(data){
      window.alert("ok");
    },
    error: function(data){
      window.alert("error");
    }
  });
}

//Sends computed path to drones
function sendToDrones(){
  $.ajax({
    type: 'post',
    url: '/pathSender',
    success: function(data){
      window.alert("ok");
    },
    error: function(data){
      window.alert("error");
    }
  });
}

//Removes selected waypoints
function clearMarkers(){
  var num_markers = markers.length;
  for(var i = 0; i < num_markers; i++){
    campus.removeLayer(markers[i]);
  }
  selected_waypoints.splice(0, selected_waypoints.length);
  markers.splice(0, markers.length);
}

//Display/Hide sectors
function setSectors(){
  if($('#cb_sectors').prop("checked")){
    for(var i = 0; i < sectors.length; i++){
      sectors[i].addTo(campus);
    }
  }
  else{
    for(var i = 0; i < sectors.length; i++){
      campus.removeLayer(sectors[i]);
    }
  }
}

//Displays/Hides default waypoints
function setWaypoints(){
  if($('#cb_default_targets').prop("checked")){
    for(var i = 0; i < default_waypoints.length; i++){
      default_waypoints[i].addTo(campus);
    }
  }
  else{
    for(var i = 0; i < default_waypoints.length; i++){
      campus.removeLayer(default_waypoints[i]);
    }
  }
}
