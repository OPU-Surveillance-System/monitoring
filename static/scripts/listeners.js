function computePath(){
  $.ajax({
    type: 'post',
    url: '/pathPlanner',
    data: JSON.stringify({nb_drones: $('#nb_drones_entry').val(),
          "sectors": selected_sectors,"obstacles":non_admissible_zones}),
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

function clearMarkers(){
  var num_markers = markers.length;
  for(var i = 0; i < num_markers; i++){
    campus.removeLayer(markers[i]);
  }
  selected_waypoints.splice(0, selected_waypoints.length);
  markers.splice(0, markers.length);
}
