function simulation(){
  nb_drones = plan.length;
  drones = Array();
  for(var i = 0; i < nb_drones; i++){
    d = L.circleMarker(starting_point[i], {radius: 3, color: 'blue'}, 1).addTo(campus);
    drones.push(d);
  }
  a = 0;
  for(var i = 0; i < nb_patrol; i++){
    for(var j = 0; j < patrol_lengths[i]; j++){
      a += 1;
      try{
        update_position(i, j, a);
      }
      catch(err){
        console.log(err)
        console.log("No point for drone " + k + " at " + j);
      }
    }
  }
}

function update_position(i, j, a){
  setTimeout(function(){
    for(var k = 0; k < nb_drones; k++){
      try{
        drones[k].setLatLng(plan[k][i][j]);
      }
      catch(err){
        console.log("No point for drone " + k + " at " + j);
      }
    }
  }, a * 125);
}
