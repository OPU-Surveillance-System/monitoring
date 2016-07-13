function simulation(){
  nb_drones = plan.length;
  drones = Array();
  for(var i = 0; i < nb_drones; i++){
    d = L.circleMarker(starting_point[i], {radius: 3, color: 'white'}, 1).addTo(campus);
    drones.push(d);
  }
  a = 0;
  for(var i = 0; i < nb_patrol; i++){
    for(var j = 0; j < patrol_lengths[i]; j++){
      a += 1;
      //console.log(k + " " + " " + i + " " + j);
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
      drones[k].setLatLng(plan[k][i][j]);
    }
    //console.log("move drone " + k + " at " + plan[k][i][j]);
  }, a * 1000);
}
