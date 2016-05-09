function computePath(){
  var nb_drones = $('#nb_drones_entry').val();
  $.ajax({
    type:'get',
    url:'/pathPlanner',
    data:[nb_drones],
    dataType:'json',
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
    campus.removeLayer(selected_sectors[i][1]);
  }
  selected_sectors.splice(0, selected_sectors.length);
}
