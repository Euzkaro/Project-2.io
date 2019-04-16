// Retrieve data from Heroku
// Populate html table from data set

// Initial build with default United States woeid
states = [];
buildLocTable();

//######################################################################################
// Build trend table


function buildLocTable(woeid = 23424977) {
  const proxyurl = "https://cors-anywhere.herokuapp.com/";
  const url = `https://geotweetapp.herokuapp.com/trends/top/${woeid}`;
  const fields = ["twitter_name", "twitter_tweet_name", "twitter_tweet_url", "twitter_tweet_volume"]

  d3.json(proxyurl + url, function (tableData) {

    console.log("Entering Building Trend Table");
    console.log(woeid);
  
    // Update table header with location reference
    tweetHdrNew = (tableData[0].twitter_name + " Trending Tweets") ;
    console.log(tweetHdrNew);
    d3.select("#tweetHdr").html(tweetHdrNew) ;

    // Get a reference to the table body
    var tbody = d3.select("tbody");

    // Clear existing table data
    tbody.html("");

    // Loop through data and append one table row `tr` for each object
    tableData.forEach((locTrend) => {
      var tweetID = locTrend.twitter_tweet_query;
      var row = tbody.append("tr");
      row.attr('class', 'trendRow');
      row.attr('id', tweetID);
      row.on('click', d => {

        var el = document.createElement('html');
        el.innerHTML = d.target.name;
        var trendid = d.target.getElementsByClassName('trendRow')[0].getAttribute('id');

        // Update locations - Jeff poking around where he shouldn't by adding
        // the line below - commenting it out...
        // getTweetLocations(trendid);

      });

      // remove location from table rows - now added to header 
      fields_new = ["twitter_tweet_name","twitter_tweet_url", "twitter_tweet_volume"];

      // Itereate through data and append data element `td` 
      // and data for data fields specified in the fields list above
      fields_new.forEach(f => {
          var cell = tbody.append("td");
          var urlCheck = locTrend[f].toString().slice(0, 4);
          if (urlCheck == "http") {
            link = cell.append("a");
            link.attr('href', locTrend[f]);
            link.attr('target', "_blank");
            link.text(locTrend[f]);
          } else {
            cell.text(locTrend[f]);
            cell.attr('id', tweetID);
          }
      });
    });

    // Get the element, add a click listener...
    document.getElementById("trendTbl").addEventListener("click", function (e) {
      // e.target is the clicked element!
      console.log("Trend Row", e.target.id, " was clicked!");

      //get locations with this tweet trending to update map markers
      console.log(e.target.id) ;
      getTweetLocations(e.target.id)

  });


    //Push event location woeid to an array
    var woeids = [];
    woeids.push(woeid);

    //Call function to get state for event woeid if not default United States woeid

    if (woeids[0] != 23424977) {
      getState(woeids);
    } else {
      // woeids = ["California", "Georgia", "Montana", "Colorado", "Illinois", "Florida", "Oregon", "Texas", "New York"];
      // getState() expects a list of WOEIDs, so send a list of several cities whenever U.S. is the location
      // "Los Angeles, California": 2441472,
      // "Atlanta, Georgia": 2357024,
      // "Omaha, Nebraska": 2465512,
      // "Denver, Colorado": 2391279,
      // "Chicago, Illinois": 2379574,
      // "Jacksonville, Florida": 2428344,
      // "Portland, Oregon": 2475687,
      // "Dallas, Texas": 2388929,
      // "New York New York": 2459115
      woeids = [2441472, 2357024, 2465512, 2391279, 2379574, 2428344, 2475687, 2388929, 2459115];
      getState(woeids);
    }

    // console.log("In buildTrendTbl.js in buildLocTable() function:  woeids and targetStates");
    // console.log(woeids[0]);
    // console.log(targetStates);

    //  targetStates = ["California", "Georgia", "Montana", "Colorado", "Illinois", "Florida", "Oregon", "Texas", "New York"];

  });
}

//######################################################################################

function getState(woeids) {

  // get location data from heroku
  const proxyurl = "https://cors-anywhere.herokuapp.com/";
  const url = `https://geotweetapp.herokuapp.com/locations`;

  d3.json(proxyurl + url, function (locationData) {

    states = [];
    console.log("entering GetState");
    console.log(woeids)

    // iterate through incoming array of woeids and heroku locations. Pass state name to array where there's a match.
    woeids.forEach((trending) => {
      locationData.forEach((location) => {
        if (location.woeid == trending) {
          if (states.includes(location.state_name_only)) {

          } else {
            states.push(location.state_name_only);
          }
        }
      });
    });

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

//######################################################################################

function getTweetLocations(tweetQuery) {

  // get locations where selected tweet trending from heroku
  const proxyurl = "https://cors-anywhere.herokuapp.com/";
  const url = `https://geotweetapp.herokuapp.com/locations/tweet/${tweetQuery}`;

  console.log("entering GetTweetLocations");
  console.log(tweetQuery);

  d3.json(proxyurl + url, function (tableData) {

    tweetName = tableData[0].twitter_tweet_name ;
    woeids = [];

    // Iterate through results and get
    // woeid information to build map and demographics
    tableData.forEach((locTrend) => {
      woeids.push(locTrend.woeid);
    });
    // get state names and refresh demographics
    getState(woeids);

    // color map markers where for trending cities
    console.log(tweetName);
    console.log(woeids);
    colorMarkers(woeids, tweetName);
 
  });
}