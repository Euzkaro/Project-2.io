function createPlotlyCharts(states){

	d3.json("https://raw.githubusercontent.com/Euzkaro/project2.io/master/state-demgraphics.json", function(data) {
        console.log(data)	 

// Built Chart 

	var width = 1200;
    var height = 350;
    var padding = 60;
	var dataset;
	// var user;
	// var vis;
	var xScale, yScale;   
});

	createViz();
	};

	function createViz() {

	 // create the svg containers

     vis = d3.select("body").

				append("svg:svg")

                .attr("width", width)

                .attr("height", height);
              

     // define the x scale

     xScale = d3.time.scale().domain([d3.min(dataset, function(d) { return d['created_at_d3']; }),

									d3.max(dataset, function(d) { return d['created_at_d3']; })])

									.range([padding, width - padding * 2]);           

	

	// define the y scale
	
	 yScale = d3.scale.linear().domain([d3.min(dataset, function(d) { return d['tweets']; }),

									d3.max(dataset, function(d) { return d['tweets']; })])

									.range([height - padding, padding]);    

                 //the y value of zero is at the top of chart and increases downward.

	
        // define the y axis

        var yAxis = d3.svg.axis()

            .orient("left")

            .scale(yScale);

        

        // define the y axis

        var xAxis = d3.svg.axis()

            .orient("bottom")

            .scale(xScale);

            

        // draw y axis with labels and move in from the size by the amount of padding

        vis.append("g")

            .attr("transform", "translate("+padding+",0)")

            .attr("class","yaxis")

            .call(yAxis);



        // draw x axis with labels and move to the bottom of the chart area

        vis.append("g")

            .attr("class", "xaxis")   // a class so it can be used to select only xaxis labels  below

            .attr("transform", "translate(0," + (height - padding) + ")")

            .call(xAxis);

            

        // now rotate text on x axis



       vis.selectAll(".xaxis text") 

          .attr("transform", function(d) {

              return "translate(" + this.getBBox().height*-2 + "," + this.getBBox().height + ")rotate(-45)";

        });

        

       showData(); 

       showUser();

    };

	function showData() {

		

		vis.selectAll('circles').data(dataset).enter().append('circle').attr('cx',function(d){ return xScale(d['created_at_d3']);})

			.attr('cy', function(d){ return yScale(d['tweets']);}).attr('r',2)

			.on("mouseover", function(d) {

			// get this bar's x/y values, then augment for the tooltip

			var xPosition = parseFloat(d3.select(this).attr("cx") - 100);

			var yPosition = parseFloat(d3.select(this).attr("cy")) / 2 + height / 2;

			// update the tooltip position and value

			d3.select("#tooltip")

			.style("left", xPosition + "px")

			.style("top", yPosition + "px")

			.select("#value")

			.html(function() {				

				if(d['hashtags'].length > 0) {

				

					// a function to remove duplicates in the hashtags array

					var fUnique = function (a) {return a.sort().filter(function(item, pos, ary) {

						return !pos || item != ary[pos - 1];

						})

					};

				

					return(' Date: ' + d['created_at'] + '<br>' + 'Nº Tweets: ' + d['tweets']  + '<br>' + ' Hashtags used: ' + fUnique(d['hashtags']));

					}

				else {

					return(' Date: ' + d['created_at'] + '<br>' + 'Nº Tweets: ' + d['tweets']  + '<br>' + ' Hashtags used: none');

				} 

			 }

				 );

			// show the tooltip

			d3.select("#tooltip").classed("hidden", false);

			})

			// hide the tooltip

			.on("mouseout", function() {

			// hide the tooltip

			d3.select("#tooltip").classed("hidden", true);

			});

			

		var tweetLine = d3.svg.line()

			.x(function(d) { return xScale(d['created_at_d3'])})

			.y(function(d) { return yScale(d['tweets'])});	

		

		vis.append("path")

			.attr("d",tweetLine(dataset)).attr("fill","none").attr("stroke","green")

			.attr("stroke-width",1);

		

	};

	

	// function showUser() {



	// 	d3.select("body").append("p").text("User: @" + user['user']);

	// 	d3.select("body").append("p").text("Date: " + user['date']);

	// }	