function createMap(trendLocMarkers) {

    //Create the base layers that will be the background of our map
    var lightmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/light-v9/tiles/256/{z}/{x}/{y}?access_token={accessToken}", {
        attribution: "Map data &copy; <a href=\"http://openstreetmap.org\">OpenStreetMap</a> contributors, <a href=\"http://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"http://mapbox.com\">Mapbox</a>",
        maxZoom: 10,
        id: "mapbox.light",
        accessToken: API_KEY
    });

    //var votes = createVoters();


    var states = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/light-v9/tiles/256/{z}/{x}/{y}?access_token={accessToken}", {
        attribution: "Map data &copy; <a href=\"http://openstreetmap.org\">OpenStreetMap</a> contributors, <a href=\"http://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"http://mapbox.com\">Mapbox</a>",
        maxZoom: 4,
        //minZoom:10,
        id: "mapbox.states",
        accessToken: API_KEY
    });

    // var demographics1 = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/light-v9/tiles/256/{z}/{x}/{y}?access_token={accessToken}", {
    //     attribution: "Map data &copy; <a href=\"http://openstreetmap.org\">OpenStreetMap</a> contributors, <a href=\"http://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"http://mapbox.com\">Mapbox</a>",
    //     maxZoom: 4,
    //     id: "mapbox.demographics1",
    //     accessToken: API_KEY
    // });


    // Create a baseMaps object to hold the lightmap layer
    var baseMaps = {
        "States": states,
        "Light": lightmap
        //"Voters": ChoroMap

    };

    // Create an overlayMaps object to hold the trend location layer
    var overlayMaps = {
        "Trend Locations": trendLocMarkers

    };

    // Create the map object with options
    var map = L.map("map", {
        center: [38.381266, -97.922211],
        zoom: 4,
        layers: [states, trendLocMarkers]
    });

    //   Create a layer control, pass in the baseMaps and overlayMaps. Add the layer control to the map
    L.control.layers(baseMaps, overlayMaps, {
        collapsed: true
    }).addTo(map);

    var statesData = "https://raw.githubusercontent.com/Euzkaro/project2.io/master/state-demgraphics.json"
    var votes = d3.json(statesData, function (data) {

        // Create a new choropleth layer
        geojson = L.choropleth(data, {

            // Define what  property in the features to use
            valueProperty: "Black",

            // Set color scale  
            scale: ["#c60b0b", "#2b0bc6"],

            // Number of breaks in step range
            steps: 5,
            maxZoom: 10,
            // q for quartile, e for equidistant, k for k-means
            mode: "q",
            style: {
                // Border color
                color: "#fff",
                weight: 1,
                fillOpacity: 0.8
            }

            //     // Binding a pop-up to each layer
            //         onEachFeature: function(feature, layer) {
            //           layer.bindPopup("<h1>" + feature.properties.name + "</h1>" + "Population: " + feature.properties.Population + "<br> Democrat Voters:<br>" +
            //              feature.properties.Democrat + "%");
            //         }
        }).addTo(map);

        // Set up the legend
        var legend = L.control({ position: "bottomright" });
        legend.onAdd = function () {
            var div = L.DomUtil.create("div", "info legend");
            var limits = geojson.options.limits;
            var colors = geojson.options.colors;
            var labels = [];

            // Add min & max
            var legendInfo = "<h4>Political Leaning (%)</h4>" +
                "<div class=\"labels\">" +
                "<div class=\"min\">" + limits[0] + "</div>" +
                "<div class=\"max\">" + limits[limits.length - 1] + "</div>" +
                "</div>";

            div.innerHTML = legendInfo;

            limits.forEach(function (limit, index) {
                labels.push("<li style=\"background-color: " + colors[index] + "\"></li>");
            });

            div.innerHTML += "<ul>" + labels.join("") + "</ul>";
            return div;
        };

        // Adding legend to the map
        //legend.addTo(map);

    });

    //##################################################################################
    //   //GeoData State Level
    //##################################################################################

    var statesData = "https://raw.githubusercontent.com/Euzkaro/project2.io/master/state-demgraphics.json"

    // //   Create a layer control, pass in the baseMaps and overlayMaps. Add the layer control to the map
    // L.control.layers(baseMaps, overlayMaps, {
    //     collapsed: false
    // }).addTo(map);

    // Add information to states layer
    // Grabbing our GeoJSON data..
    d3.json(statesData, function (data) {
        // Creating a geoJSON layer with the retrieved data
        L.geoJson(data, {
            style: {
                fillOpacity: 0.0,
                color: "white",
                weight: 1
            },
            // Called on each feature
            onEachFeature: function (feature, layer) {
                // Set mouse events to change map styling
                layer.on({
                    // When a user's mouse touches a map feature, the mouseover event calls this function, that feature's opacity changes to 90% so that it stands out
                    mouseover: function (event) {
                        layer = event.target;
                        layer.setStyle({
                            fillOpacity: 0.9,
                            color: "#4E2A84"
                        });
                    },
                    // When the cursor no longer hovers over a map feature - when the mouseout event occurs - the feature's opacity reverts back to 50%
                    mouseout: function (event) {
                        layer = event.target;
                        layer.setStyle({
                            fillOpacity: 0.00,
                            color: "#fff"//"#4E2A84"
                        });
                    },
                    // When a feature (state) is clicked, it is enlarged to fit the screen
                    click: function (event) {
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
                    // "<br> Whites (%): " + feature.properties.White +
                    // "<br> Blacks (%): " + feature.properties.Black +
                    // "<br> Asians (%): " + feature.properties.Asian +
                    // "<br> Latinos (%): " + feature.properties.Latino +
                    // "<br> Natives (%): " + feature.properties.Native +
                    "<br> Unemployment (%): " + feature.properties.Unemployment +
                    '<br><iframe width="321px" height="548px" src="' + feature.properties.image + '"></iframe>' +
                    "</p>");
            }
        }).addTo(map);
    });
};
// //######################################################################################
// // Choropleth
// //######################################################################################
// // Link to GeoJSON
// 

// function createVoters() {
//     var statesData = "https://raw.githubusercontent.com/Euzkaro/project2.io/master/state-demgraphics.json"
//     var votes = d3.json(statesData, function (data) {

//         // Create a new choropleth layer
//         geojson = L.choropleth(data, {

//             // Define what  property in the features to use
//             valueProperty: "Black",

//             // Set color scale  
//             scale: ["#c60b0b", "#2b0bc6"],

//             // Number of breaks in step range
//             steps: 10,

//             // q for quartile, e for equidistant, k for k-means
//             mode: "q",
//             style: {
//                 // Border color
//                 color: "#fff",
//                 weight: 1,
//                 fillOpacity: 0.8
//             }

//         //     // Binding a pop-up to each layer
//         //         onEachFeature: function(feature, layer) {
//         //           layer.bindPopup("<h1>" + feature.properties.name + "</h1>" + "Population: " + feature.properties.Population + "<br> Democrat Voters:<br>" +
//         //              feature.properties.Democrat + "%");
//         //         }
//         });//.addTo(map);

//         // // Set up the legend
//         // var legend = L.control({ position: "bottomright" });
//         // legend.onAdd = function () {
//         //     var div = L.DomUtil.create("div", "info legend");
//         //     var limits = geojson.options.limits;
//         //     var colors = geojson.options.colors;
//         //     var labels = [];

//         //     // Add min & max
//         //     var legendInfo = "<h1>Democrat Voters (%)</h1>" +
//         //         "<div class=\"labels\">" +
//         //         "<div class=\"min\">" + limits[0] + "</div>" +
//         //         "<div class=\"max\">" + limits[limits.length - 1] + "</div>" +
//         //         "</div>";

//         //     div.innerHTML = legendInfo;

//         //     limits.forEach(function (limit, index) {
//         //         labels.push("<li style=\"background-color: " + colors[index] + "\"></li>");
//         //     });

//         //     div.innerHTML += "<ul>" + labels.join("") + "</ul>";
//         //     return div;
//         // };

//         // // Adding legend to the map
//         // legend.addTo(map);

//     });
//     return (votes);
// };



function createDemographicsChart(a_data, a_y_key, a_x_key, a_state_name = null, a_chart_index = 0) {
// Function to draw a Demographics Chart based upon a selected
// location (or state?)
//
// Arguments:
//    a_data: Data to use for the chart (array of objects)
//    a_y_key: Key for the y-axis data to plot
//    a_x_key: Key for the x-axis data to plot
//    a_state_name: Name of the state to use for the chart
//    a_chart_id: The id of the chart to place the chart (e.g., "demo_chart_0") 

    // Process arguments

    // Valid chart index values are 0 to 2 inclusive
    chart_index = int(a_chart_index);
    chart_index = chart_index < 0 ? 0 : chart_index;
    chart_index = chart_index > 2 ? 2 : chart_index;
    chart_id = `demo_chart_${chart_index}`

    // For now, assume we have well-behaved data and x and y axis keys
    // Sample Data:
    // a_data = {
    //     "type":"Feature",
    //     "id":"01",
    //     "properties":
    //         {
    //             "name":"Alabama",
    //             "Republican":62.9,
    //             "Democrat":34.6,
    //             "Population":4706548,
    //             "BachelorDegree":15.39,
    //             "HighSchool":76.78,
    //             "White":66.65,
    //             "Black":28.23,
    //             "Native":0.61,
    //             "Asian":0.55,
    //             "Latino":2.77,
    //             "Unemployment":0.09,
    //             "image": "https://embed.datausa.io/profile/geo/alabama/economy/income/?viz=True",
    //             "density":94.65
    //         },
    //
    //     "geometry":
    //         {
    //             "type":"Polygon",
    //             "coordinates":[[[-87.359296,35.00118],[-85.606675,34.984749],[-85.431413,34.124869],[-85.184951,32.859696],[-85.069935,32.580372],[-84.960397,32.421541],[-85.004212,32.322956],[-84.889196,32.262709],[-85.058981,32.13674],[-85.053504,32.01077],[-85.141136,31.840985],[-85.042551,31.539753],[-85.113751,31.27686],[-85.004212,31.003013],[-85.497137,30.997536],[-87.600282,30.997536],[-87.633143,30.86609],[-87.408589,30.674397],[-87.446927,30.510088],[-87.37025,30.427934],[-87.518128,30.280057],[-87.655051,30.247195],[-87.90699,30.411504],[-87.934375,30.657966],[-88.011052,30.685351],[-88.10416,30.499135],[-88.137022,30.318396],[-88.394438,30.367688],[-88.471115,31.895754],[-88.241084,33.796253],[-88.098683,34.891641],[-88.202745,34.995703],[-87.359296,35.00118]]]
    //         }
    //     }

    // For now, assume we have well-behaved state name

    var eyeColor = ["Brown", "Brown", "Brown", "Brown", "Brown",
        "Brown", "Brown", "Brown", "Green", "Green",
        "Green", "Green", "Green", "Blue", "Blue",
        "Blue", "Blue", "Blue", "Blue"];

    var eyeFlicker = [26.8, 27.9, 23.7, 25, 26.3, 24.8,
        25.7, 24.5, 26.4, 24.2, 28, 26.9,
        29.1, 25.7, 27.2, 29.9, 28.5, 29.4, 28.3];

    // Create the Trace
    var trace1 = {
        x: eyeColor,
        y: eyeFlicker,
        type: "bar"
    };

    // Create the data array for the plot
    var data = [trace1];

    // Define the plot layout
    var layout = {
        title: "Eye Color vs Flicker",
        xaxis: { title: "Eye Color" },
        yaxis: { title: "Flicker Frequency" }
    };

    // Plot the chart to a div tag with id "demochart0"
    Plotly.newPlot(chart_id, data, layout);
}

//######################################################################################
function createMarkers(data) {

    // Pull the "name" property off of data
    //var locations = data.name;

    // marker setup
    var BubbleIcon = L.Icon.extend({
        options: {
            iconSize: [30, 50],
            iconAnchor: [15, 50],
            popupAnchor: [-3, -76]
        }
    });

    var greenIcon = new BubbleIcon({ iconUrl: 'C:/Users/agarb/Documents/Bootcamp/Homework/geotweet/Project-2.io/static/images/MapMarker_Bubble_Green.png' });
    var whiteIcon = new BubbleIcon({ iconUrl: 'static/images/MapMarker_Bubble_White.png' });
    var redIcon = new BubbleIcon({ iconUrl: '../images/MapMarker_Bubble_Red.png' });
    var blueIcon = new BubbleIcon({ iconUrl: '../images/MapMarker_Bubble_Blue.png' });
    var azureIcon = new BubbleIcon({ iconUrl: '../images/MapMarker_Bubble_Azure.png' });
    var orangeIcon = new BubbleIcon({ iconUrl: '../images//MapMarker_Bubble_Orange.png' });

    // Initialize an array to hold trend location markers
    var trendLocMarkers = [];

    // Loop through the sample location array
    for (var index = 0; index < data.length; index++) {
        var location = data[index];
        console.log(location)

        // For each location, create a marker and bind a popup with the location name
        var locationMarker = L.marker([location.latitude, location.longitude], { icon: whiteIcon })
            .bindPopup("<h3>" + location.name_only + "<h3><h3 class=\"locate\" id=\"" + location.woeid + "\">" + location.state_name_only + "<h3>")
            .on('click', d => {

                var el = document.createElement('html');
                el.innerHTML = d.target._popup._container;
                var woeid = d.target._popup._container.getElementsByClassName('locate')[0].getAttribute('id');

                console.log(woeid);

                const proxyurl = "https://cors-anywhere.herokuapp.com/";
                const url = `https://geotweetapp.herokuapp.com/trends/top/${woeid}`;
                const fields = ["twitter_name", "twitter_tweet_name", "twitter_tweet_url", "twitter_tweet_volume"]

                d3.json(proxyurl + url, function (tableData) {
                    console.log(tableData);

                    // Get a reference to the table body
                    var tbody = d3.select("tbody");
                    console.log(tbody.html());
                    tbody.html("");
                    console.log(tbody.html());
                    // Loop through data and append one table row `tr` for each object
                    tableData.forEach((locTrend) => {
                        var row = tbody.append("tr");
                        // Append data elements `td` for each object and enter data values
                        //   Object.entries(locTrend).forEach(([key, value]) => {
                        fields.forEach(f => {
                            var cell = tbody.append("td");
                            cell.text(locTrend[f]);
                        });
                        // var cell = tbody.append("td");
                        // cell.text(value);
                    });
                });
            });
    

        // Add the marker to the location Markers array
        trendLocMarkers.push(locationMarker);
        // console.log(trendLocMarkers);
    };

    // Create a layer group made from the location markers array, pass it into the createMap function
    createMap(L.layerGroup(trendLocMarkers));
};


// Retrieve data from sample data file and call marker function
var locationData = trendLocations;

createMarkers(locationData);

var statesData = "https://raw.githubusercontent.com/Euzkaro/project2.io/master/state-demgraphics.json"

createDemographicsChart(statesData, "abc", "def", a_state_name = null, a_chart_index = 0); 





