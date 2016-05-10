function computePath(){
  for(var i = 0; i < selected_sectors.length; i++){
    console.log(selected_sectors[i]);
  }
  $.ajax({
    type:'post',
    url:'/pathPlanner',
    data:JSON.stringify({nb_drones: $('#nb_drones_entry').val(),
          "sectors": selected_sectors}),
    //dataType:'json',
    contentType: "application/json; charset=utf-8",
    success: function(data){
      window.alert("ok");
    },
    error: function(data){
      window.alert("not ok");
    }
  });
}

function clearMarkers(){
  var bound = selected_sectors.length;
  for(var i = 0; i < bound; i++){
    campus.removeLayer(markers[i][1]);
  }
  selected_sectors.splice(0, selected_sectors.length);
  markers.splice(0, markers.length);
}
