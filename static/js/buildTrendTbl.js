// Retrieve data from Heroku
// Populate html table from data set

// Initial build with default United States woeid
buildLocTable();

// Build trend table
function buildLocTable(woeid = 23424977) {
  const proxyurl = "https://cors-anywhere.herokuapp.com/";
  const url = `https://geotweetapp.herokuapp.com/trends/top/${woeid}`;
  const fields = ["twitter_name", "twitter_tweet_name", "twitter_tweet_url", "twitter_tweet_volume"]

  d3.json(proxyurl + url, function (tableData) {

    // Get a reference to the table body
    var tbody = d3.select("tbody");

    // Clear existing table data
    tbody.html("");

    // Loop through data and append one table row `tr` for each object
    tableData.forEach((locTrend) => {
      var row = tbody.append("tr");

      // Itereate through data and append data element `td` 
      // and data for data fields specified in the fields list above
      fields.forEach(f => {
        var cell = tbody.append("td");
        cell.text(locTrend[f]);
      });

    });

    //Push event location woeid to an array
    var woeids = [];
    woeids.push(woeid);

    //Call function to get state for event woeid if not default United States woeid
    if (woeids[0] != 23424977) {
      var targetStates = getState(woeids);
    }
    console.log(targetStates);

    return targetStates; //replace with call to function that will  build demographic charts based on targetState argument 
  });
}


function getState(woeids) {

  // get location data from heroku
  const proxyurl = "https://cors-anywhere.herokuapp.com/";
  const url = `https://geotweetapp.herokuapp.com/locations`;

  d3.json(proxyurl + url, function (locationData) {

    states = [];

    // iterate through incoming array of woeids and heroku locations. Pass state name to array where there's a match.
    woeids.forEach((trending) => {
      locationData.forEach((location) => {
        if (location.woeid == trending) {
          states.push(location.state_name_only)
        }
      });
    });

    console.log(states);
    return states;
  });
}
