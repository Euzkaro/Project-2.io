// Retrieve data from Heroku


function getData() {

    const proxyurl = "https://cors-anywhere.herokuapp.com/";
    const url = "https://geotweetapp.herokuapp.com/trends/top/2379574";

    var trendData ; 
    //var trendData = fetch(proxyurl + url).then ;

    runFetch()

    // fetch(proxyurl + url)
    // .then(function(response) {
    //   return response.json();
    // })
    // .then(function(trendData) { 
    //   console.log(JSON(trendData));
    // });

    async function runFetch(){
        fetch(proxyurl + url)
        .then(res => res.json())
        .then(data => trendData = data)
        .then(() => console.log(trendData));
    }

    d3.json(async function runFetch(){
        fetch(proxyurl + url)
        .then(res => res.json())
        .then(data => trendData = data)
        .then(() => console.log(trendData));
    }



    return(trendData);

}        
    delete trendData.twitter_as_of;
    delete trendData.twitter_created_at;
    delete trendData.twitter_tweet_promoted_content;
    delete trendData.twitter_tweet_query;
    delete trendData.woeid;

    // trendData.forEach((trend) => {
    //     console.log(trend);
    //     // Get the entries for each object in the array
    //     Object.entries(trend).forEach(([key, value]) => {
    //         // Log the key and value
    //         console.log(`Key: ${key} and Value ${value}`);
    //     });
    // });

    // Object.keys(trendData).forEach(function(key) {
    //     var value = trendData[key];
    //     console.log(value);
    //   });

// var trendData = [{"twitter_as_of":"2019-03-30T02:10:14Z","twitter_created_at":"2019-03-30T02:07:05Z","twitter_name":"Chicago","twitter_tweet_name":"Carolina","twitter_tweet_promoted_content":null,"twitter_tweet_query":"Carolina","twitter_tweet_url":"http://twitter.com/search?q=Carolina","twitter_tweet_volume":75729.0,"woeid":2379574},{"twitter_as_of":"2019-03-30T02:10:14Z","twitter_created_at":"2019-03-30T02:07:05Z","twitter_name":"Chicago","twitter_tweet_name":"Auburn","twitter_tweet_promoted_content":null,"twitter_tweet_query":"Auburn","twitter_tweet_url":"http://twitter.com/search?q=Auburn","twitter_tweet_volume":57739.0,"woeid":2379574},{"twitter_as_of":"2019-03-30T02:10:14Z","twitter_created_at":"2019-03-30T02:07:05Z","twitter_name":"Chicago","twitter_tweet_name":"#RockHall2019","twitter_tweet_promoted_content":null,"twitter_tweet_query":"%23RockHall2019","twitter_tweet_url":"http://twitter.com/search?q=%23RockHall2019","twitter_tweet_volume":30707.0,"woeid":2379574},{"twitter_as_of":"2019-03-30T02:10:14Z","twitter_created_at":"2019-03-30T02:07:05Z","twitter_name":"Chicago","twitter_tweet_name":"Elite 8","twitter_tweet_promoted_content":null,"twitter_tweet_query":"%22Elite+8%22","twitter_tweet_url":"http://twitter.com/search?q=%22Elite+8%22","twitter_tweet_volume":21049.0,"woeid":2379574},{"twitter_as_of":"2019-03-30T02:10:14Z","twitter_created_at":"2019-03-30T02:07:05Z","twitter_name":"Chicago","twitter_tweet_name":"#Ultra2019","twitter_tweet_promoted_content":null,"twitter_tweet_query":"%23Ultra2019","twitter_tweet_url":"http://twitter.com/search?q=%23Ultra2019","twitter_tweet_volume":17198.0,"woeid":2379574}] ;


// delete trendData.twitter_as_of;

// function getDates(trendData) {
//     dates = [];
//     for (var i = 0; i < trendData.length; i++ ) {
//         dates.push(trendData[i].twitter_as_of);
//     }
//     return dates;
// };


// delete trendData.twitter_as_of;
// delete trendData.twitter_created_at;
// delete trendData.twitter_tweet_promoted_content;
// delete trendData.twitter_tweet_query;
// delete trendData.woeid;

// for (i = 0; i < trendData.length; i++) {
//     console.log ("The number is " + i );
//     console.log (trendData)

//return (trendData);