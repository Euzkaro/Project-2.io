// Creating map object
var map = L.map("main-map").setView([39.381266, -97.922211], 4);
 
  
  // Adding tile layer
  L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
    attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
    maxZoom: 18,
    id: "mapbox.streets",
    accessToken: "pk.eyJ1Ijoia3VsaW5pIiwiYSI6ImNpeWN6bjJ0NjAwcGYzMnJzOWdoNXNqbnEifQ.jEzGgLAwQnZCv9rA6UTfxQ"
  }).addTo(map);



//##################################################################################
//   //GeoData State Level
//##################################################################################
//var statesData = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
  var statesData = "https://raw.githubusercontent.com/Euzkaro/project2.io/master/state-demgraphics.json"


// Grabbing our GeoJSON data..
d3.json(statesData, function(data) {
  // Creating a geoJSON layer with the retrieved data
  L.geoJson(data, {
    // Called on each feature
    onEachFeature: function(feature, layer) {
      // Set mouse events to change map styling
      layer.on({
        // When a user's mouse touches a map feature, the mouseover event calls this function, that feature's opacity changes to 90% so that it stands out
        mouseover: function(event) {
          layer = event.target;
          layer.setStyle({
            fillOpacity: 0.9,
            color: "#4E2A84"
          });
        },
        // When the cursor no longer hovers over a map feature - when the mouseout event occurs - the feature's opacity reverts back to 50%
        mouseout: function(event) {
          layer = event.target;
          layer.setStyle({
            fillOpacity: 0.5,
            color: "#4E2A84"
          });
        },
        // When a feature (state) is clicked, it is enlarged to fit the screen
        click: function(event) {
          map.fitBounds(event.target.getBounds());
        }
      });
      // Giving each feature a pop-up with information pertinent to it
      layer.bindPopup("<h1>" + feature.properties.name + 
      "</h1> <hr> <p>Population: " + 
      feature.properties.Population + 
      "<br> Republican Voters (%): " + feature.properties.Republican + 
      "<br> Democrat Voters (%): " + feature.properties.Democrat +
      "<br> College Graduates (%): " + feature.properties.BachelorDegree +
      "<br> High School Graduates (%): " + feature.properties.HighSchool +
      "<br> Whites (%): " + feature.properties.White +
      "<br> Blacks (%): " + feature.properties.Black +
      "<br> Asians (%): " + feature.properties.Asian +
      "<br> Latinos (%): " + feature.properties.Latino +
      "<br> Natives (%): " + feature.properties.Native +
      "<br> Unemployment (%): " + feature.properties.Unemployment +
      "</p>");

    }
  }).addTo(map);
});
//##################################################################################



  