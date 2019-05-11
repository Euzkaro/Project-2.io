
function getLinearRegr(a_x_list, a_y_list) {
    // Function to calculate the linear regression of the data
    // Source: https://github.com/Tom-Alexander/regression-js

    // Need at least 2 points to return a trend line
    if (a_x_list.length < 2) {
        // Only one point sent, so return an empty list
        return [];
    }

    // Build the input array to the linear regression function as
    // an array of coordinate point arrays

    var coordList = [];
    for (i = 0; i < a_x_list.length; ++i) {
        coordList.push([a_x_list[i], a_y_list[i]]);
    }
    // console.log("Input Array: ", coordList);

    // Calculate the linear regression
    // Input Arguments:
    // coordList: A list of [x, y] pairs over which the linear regresison will be calculated 

    // Return Values:
    // equation: an array containing the coefficients of the equation [slope, y-intercept]
    // string: A string representation of the equation
    // points: an array containing the predicted data in the domain of the input
    // r2: the coefficient of determination (R2)
    // predict(x): This function will return the predicted value as a coordinate point [x_input, y_predicted]
    var result = regression.linear(coordList);

    // console.log("Linear Regression:", result);

    // Use the list of x-values to generate predicted
    // y-values that define the trend line
    var predicted_y_list = [];
    for (i = 0; i < a_x_list.length; ++i) {
        // Push a coordinate on the trend line to the trendLine list
        // Note: the result.predict() function returns a coordinate [x, predicted_y]
        // So grab just the predicted_y part.
        predicted_y_list.push( (result.predict(a_x_list[i]))[1] );
    }

    // console.log("x-list and predicted y-list:");
    // console.log(a_x_list);
    // console.log(predicted_y_list);

    return { 'x_list': a_x_list, 'predicted_y_list': predicted_y_list };
}

function createAllDemographicsCharts(a_state_list) {
    // Function to display 3 demographics charts based upon a list of
    // states names provided as arguments

    // console.log("In demographicsChart.js: createAllDemographicsCharts(): Preparing to chart for states:");
    // console.log(a_state_list);

    // Function to read all the demographics data into an array of objects and return it for others to use
    var statesDataURL = "https://raw.githubusercontent.com/Euzkaro/project2.io/master/state-demgraphics.json"

    d3.json(statesDataURL, d => {
        // Get the data from the web repository
        var data_list = d.features;

        // console.log("In demographicsCharts.js - inside the d3.json(): statesDemoData is");
        // console.log("The data list from states demographic file on the web");
        // console.log(data_list);

        // Display the demographics charts

        createDemographicsChart(data_list, "Democrat", "density", a_state_list, 0);
        // createDemographicsChart(data_list, "Republican", "HighSchool", a_state_list, 0);
        // createDemographicsChart(data_list, "Republican", "Unemployment", a_state_list, 1);
        // createDemographicsChart(data_list, "Republican", "Population", a_state_list, 2);
    });
}


function createDemographicsChart(a_data_list, a_x_value, a_y_value, a_state_list = ["Illinois"], a_chart_index = 0) {
    // Function to draw a DecreateDemographicsChartmographics Chart based upon a selected
    // location (or state?)
    //
    // Arguments:
    //    a_data_list: Data list containing demographics info
    //    a_y_key: Key for the y-axis data to plot
    //    a_x_key: Key for the x-axis data to plot
    //    a_state_list: Name of the state to use for the chart
    //    a_chart_index: The id of the chart to place the chart (e.g., "demo_chart_0") 

    // console.log("In demographicsChart.js: createDemographicsChart(): Preparing to chart for states:");
    // console.log(a_state_list);

    // Constants
    const stateAbbrs = {
        'Arizona': 'AZ',
        'Alabama': 'AL',
        'Alaska': 'AK',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY',
        'United States': 'USA'
    };

    // Use this plotConfig object to provide plot configuration settings
    // depending upon which field is used to drive an axis
    const plotConfig = {
        "Republican": { axis_label: "Republican (%)", scale_factor: 1.0, max_range: 100 },
        "Democrat": { axis_label: "Democrat (%)", scale_factor: 1.0, max_range: NaN },
        "Population": { axis_label: "Total Population", scale_factor: 1, max_range: NaN },
        "BachelorDegree": { axis_label: "Max. Education is Bachelors Degree (%)", scale_factor: 1.0, max_range: 100 },
        "HighSchool": { axis_label: "Max. Education is High School (%)", scale_factor: 1.0, max_range: 100 },
        "White": { axis_label: "Racial Group: White (%)", scale_factor: 1.0, max_range: 100 },
        "Black": { axis_label: "Racial Group: Black (%)", scale_factor: 1.0, max_range: 100 },
        "Native": { axis_label: "Racial Group: Native American (%)", scale_factor: 1.0, max_range: 100 },
        "Asian": { axis_label: "Racial Group: Asian (%)", scale_factor: 1.0, max_range: 100 },
        "Latino": { axis_label: "Racial Group: Latino (%)", scale_factor: 1.0, max_range: 100 },
        "Unemployment": { axis_label: "Unemployment Rate (%)", scale_factor: 100.0, max_range: NaN },
        "density": { axis_label: "Population Density (people/sq. mile)", scale_factor: 1.0, max_range: NaN }
    };

    // Process arguments

    // Valid chart index values are 0 to 2 inclusive
    chart_index = Number(a_chart_index);
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


    // Define the scatter chart based upon:
    // x-axis and y-axis factors provided in the arguments

    // Get the scatter plot points by checking each element in the demographics data
    x_list = [];
    y_list = [];
    label_list = [];

    // Remove any entries that are not states in the demographics list
    temp_list = []
    a_state_list.forEach(s => {
        // If this state is a key in the demographic list, keep it!
        if (s in stateAbbrs) {
            temp_list.push(s);
        }
    });
    a_state_list = temp_list;

    // If the states list is empty, populate it with "Illinois"
    if (a_state_list.length == 0) {
        a_state_list = ["Illinois"];
    }

    // Use the data list passed into the function
    data_list = a_data_list;

    // Loop through each state for a match
    data_list.forEach(s => {
        // Only use this data item if the state matches one in the argument list of states
        if (a_state_list.includes(s.properties['name'])) {
            x_list.push(s.properties[a_x_value] * plotConfig[a_x_value]['scale_factor']);
            y_list.push(s.properties[a_y_value] * plotConfig[a_y_value]['scale_factor']);
            label_list.push(stateAbbrs[s.properties['name']]);

        }
    });

    // Create the Trace
    var trace1 = {
        x: x_list,
        y: y_list,
        name: 'State Demographics',
        text: label_list,
        textposition: 'center',
        textfont: {
            family: 'Arial, sans-serif',
            weight: 600,
            size: 15
        },
        mode: "markers+text",
        type: "scatter",
        marker: {
            size: 40,
            opacity: 0.5
        }
    };


    // Create the data array for the plot
    var data = [trace1];

    // Generate a trend line if at least 2 data points
    // (Maybe minimum should be 3 data points for this to be interesting...)

    if (x_list.length > 1) {
        // Get a list of x and predicted y values based
        // upon linear regression of the x and y values
        // Returns: { 'x_list': a_x_list, 'predicted_y_list': predicted_y_list }
        var results = getLinearRegr(x_list, y_list);

        // Create the Trace
        var trace_trend = {
            x: results.x_list,
            y: results.predicted_y_list,
            name: 'Linear Trend Line',
            textfont: {
                family: 'Arial, sans-serif',
                weight: 600,
                size: 15
            },
            mode: "lines",
            line: {
                color: 'blue',
                opacity: 0.5,
                width: 3,
                dash: '5 5'
            }
        };

        data.push(trace_trend);
    }

    // console.log("In demographicsCharts.js: createDemographicsChart(): trace_trend");
    // console.log(data);

    // Define the plot layout
    var layout = {
        title: `${plotConfig[a_y_value]['axis_label']} vs. ${plotConfig[a_x_value]['axis_label']}`,
        showlegend: true,
        legend: {
            "orientation": "v",
            x: 0.3, y: -0.5
        }
    };

    // Set the max range base upon the data
    if (isNaN(plotConfig[a_x_value]['max_range'])) {
        // If no max range provided, set the range automatically based upon the data
        // Range will be set automatically by Plotly
        layout['xaxis'] = { title: `${plotConfig[a_x_value]['axis_label']}` };
    } else {
        // If max range provided, set the range accordingly
        // Range will be [ -10, The larger of the specified rage value*1.2 or 100 ]
        xMaxRange = Math.max(100, plotConfig[a_x_value]['max_range'] * 1.2);
        layout['xaxis'] = { title: `${plotConfig[a_x_value]['axis_label']}`, range: [-10, xMaxRange] };
    }

    // Set the max range base upon the data
    if (isNaN(plotConfig[a_y_value]['max_range'])) {
        // If no max range provided, set the range automatically based upon the data
        // Range will be set automatically by Plotly
        layout['yaxis'] = { title: `${plotConfig[a_y_value]['axis_label']}` };
        // console.log("Setting Y axis layout for an item with max_range = null ");
        // console.log(layout);
    } else {
        // If max range provided, set the range accordingly
        // Range will be [ -10, The larger of the specified rage value*1.2 or 100 ]
        yMaxRange = Math.max(100, plotConfig[a_y_value]['max_range'] * 1.2);
        layout['yaxis'] = { title: `${plotConfig[a_y_value]['axis_label']}`, range: [-10, yMaxRange] };
    }

    // console.log("In demographicsCharts.js: layout");
    // console.log(layout);

    // Plot the chart to a div tag with id chart_id
    Plotly.newPlot(chart_id, data, layout);

}