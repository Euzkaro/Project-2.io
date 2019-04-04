// Populate html table from data set
// retrieve data from data file

// var tableData = getData();
const proxyurl = "https://cors-anywhere.herokuapp.com/";
const url = "https://geotweetapp.herokuapp.com/trends/top/2379574";

d3.json(proxyurl + url, function (tableData) {
    console.log(tableData);

    // Get a reference to the table body
    var tbody = d3.select("tbody");

    // Loop through data and append one table row `tr` for each object
    tableData.forEach((locTrend) => {
      var row = tbody.append("tr");

      // Append data elements `td` for each object and enter data values
      Object.entries(locTrend).forEach(([key, value]) => {
        var cell = tbody.append("td");
        cell.text(value);
      });
    });
  })

// var tableData = chicagoTrending;



// $("#table tr").click(function(){
//   $(this).addClass('selected').siblings().removeClass('selected');    
//   var value=$(this).find('td:first').html();
//   alert(value);    
// });

// $('.ok').on('click', function(e){
//    alert($("#table tr.selected td:first").html());
// });

// // Allow viewer to filter based on datetime
// // Select the submit button and prevent it from refreshing
// var filter = d3.select("#filter-btn");
//   filter.on("click", function() {
//     d3.event.preventDefault();

//     // Select the input element and get the value property of the input element
//     var inputElement = d3.select("#datetime");
//     var inputValue = inputElement.property("value");

//     var filteredData = tableData.filter(sighting => sighting.datetime === inputValue);

//     // Clear existing data  
//     var clearData = [] ;

//     d3.select("tbody").selectAll("td")
//       .data(clearData)
//       .exit()
//       .remove();

//     // Repopulate with filtered data. 
//     // Set tableData to filtered data set.

//     var newData = filteredData;
//     console.log(newData)

//     // Get a reference to the table body
//     var tbody = d3.select("tbody");

//     // Loop through data and append one table row `tr` for each object
//     newData.forEach(function(sighting) {
//     var row = tbody.append("tr");

//       // Append data elements `td` for each object and enter data values
//         Object.entries(sighting).forEach(([key, value]) => {
//         var cell = tbody.append("td");
//         cell.text(value);
//       });
//     });
// });
