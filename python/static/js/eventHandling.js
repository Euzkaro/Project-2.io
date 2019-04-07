// Event Handling 
// Changes when a trend location is selected on the map

// var geojson;
// // ... our listeners


// function onEachFeature(feature, layer) {
//     layer.on({
//         _popup._content   : identifyMarker
//     });
// }

// geojson = L.trendLocations(statesData, {
//     onEachFeature: onEachFeature
// }).addTo(map);

// function identifyMarker(e) {
//     alert(e.popup._source._popup._content)
// };




// geojson = L.geoJson(...);


map.on('click', function(e) {
    alert(e.latlng);
} );


// map.on('popupopen', function(e) {
//     var marker = e.popup._source.feature.properties.markerid;
// });

function() {
    L.map.on(document, 'eventname', this._doSomething, this);
},

removeHooks: function() {
    L.DomEvent.off(document, 'eventname', this._doSomething, this);
},

_doSomething: function(event) { … }
});
map.on('popupopen', function(e) { alert(e.popup._source._popup._content); });


// function onClick(e) {alert(this.getLatLng());}

// var latlng = map.mouseEventToLatLng(event);
// console.log('Handler detected CTRL + click at ' + latlng);


// Update Card-Title when marker selected on Map


// Update Tweet values when marker selected on Map



// Event Handling 
// Changes when a trend is selected from the list


//Update map marker color and size where tweet is trending

//json pull




