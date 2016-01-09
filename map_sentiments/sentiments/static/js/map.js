//Width and height
var w = 700;
var h = 400;

//Define map projection
var projection = d3.geo.albersUsa()
                       .translate([w/2, h/2])
                       .scale([700]);

//Define default path generator
var path = d3.geo.path()
                    .projection(projection);


//Define quantize scale to sort data values into buckets of color
var color = d3.scale.linear()
                    .range(['rgb(252,141,89)','rgb(255,255,191)','rgb(145,207,96)']);
                    //Colors taken from colorbrewer.js, included in the D3 download

//Create SVG element
var svg = d3.select("body")
            .append("svg")
            .attr("width", w)
            .attr("height", h);


// declare your variable for the setInterval so that you can clear it later
var myInterval;

// set your interval
myInterval = setInterval(updateData,2000);

function updateData(){

    // Load JSON file , info : var urlScoreByStates is set server side
    d3.json(urlScoreByStates, function(data) {

        //Set input domain for color scale
        color.domain([
            d3.min(data, function(d) { return d.value; }),
            d3.max(data, function(d) { return d.value; })
        ]);

        //Load in GeoJSON data , info : var urlUsStates is set server side
        d3.json(urlUsStates, function(json) {

            //Merge the ag. data and GeoJSON
            //Loop through once for each ag. data value
            for (var i = 0; i < data.length; i++) {

                //Grab state name
                var dataState = data[i].state;

                //Grab data value, and convert from string to float
                var dataValue = parseFloat(data[i].value);

                //Find the corresponding state inside the GeoJSON
                for (var j = 0; j < json.features.length; j++) {

                    var jsonState = json.features[j].properties.name;

                    if (dataState == jsonState) {

                        //Copy the data value into the JSON
                        json.features[j].properties.value = dataValue;

                        //Stop looking through the JSON
                        break;

                    }
                }
            }

            //Bind data and create one path per GeoJSON feature
            svg.selectAll("path")
               .data(json.features)
               .enter()
               .append("path")
               .attr("d", path)
               .style("fill", function(d) {
                    //Get data value
                    var value = d.properties.value;

                    if (value) {
                        //If value exists…
                        return color(value);
                    } else {
                        //If value is undefined…
                        return "#ccc";
                    }
               });

        });

    });

}





