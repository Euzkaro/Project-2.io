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
    var targetStates = [];
    if (woeids[0] != 23424977) {
      targetStates = getState(woeids);
    }
    // console.log("In buildTrendTbl.js in buildLocTable() function:  woeids and targetStates");
    // console.log(woeids[0]);
    // console.log(targetStates);

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

    console.log("In buildTrendTbl.js in getState() function:  states");
    console.log(states);

    // Ok, this is the only place (inside this d3.json call)
    // where we're guaranteed to get 'states' populated properly
    // before making the call to create the demographics charts,
    // so doing that from here
    // NOTE: Without d3 v5 and promises, the return value
    // from this function doesn't populate in time before it
    // would be needed in demographics chart function... 
    
    // Load up the states demographics data as a list of objects
    createAllDemographicsCharts(states);

    return states;
  });
}
