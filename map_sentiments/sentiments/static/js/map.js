// Refresh size of the map
d3.select(window).on('resize', function(){ update(1);});


// Var declaration
var w;
var h;
var projection;
var path;
var svg;
//Define quantize scale to sort data values into buckets of color
var color = d3.scale.linear()
            .domain([-1, 0, 1])
            .range(['rgb(252,141,89)','rgb(255,255,191)','rgb(145,207,96)']);

/*var color = d3.scale.linear()
    .range(["red", "green"])
    .domain([-1, 1]);
*/

update(1);

// Interval to refresh data
var myInterval;

// set your interval
myInterval = setInterval(function(){ update(0); },2000);

function update(resize) {

    if (resize==1){
        newWidth = parseInt(d3.select('#map').style('width'), 10);

        //Width and height
        w = newWidth;
        h = w/2;

        d3.select("#map").attr("width", w)
                         .attr("height", h);

        d3.select("svg").remove();

        //Define map projection
        projection = d3.geo.albersUsa()
                               .translate([w/2, h/2])
                               .scale([w]);

        //Define default path generator
        path = d3.geo.path()
                           .projection(projection);

        //Create SVG element
        svg = d3.select("#map")
                    .append("svg")
                    .attr("width", w)
                    .attr("height", h);

    }

    updateData();

}

var fillState = function(d) {
                    //Get data value
                    var value = d.properties.value;

                    if (value) {
                        //If value exists…
                        return color(value);
                    } else {
                        //If value is undefined…
                        return "#ccc";
                    }
               }

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
            // Update data
            selection = svg.selectAll("path")
               .data(json.features)
               .style("fill", fillState);

            // Add new data that do not have a DOM element "path" available
            selection.enter()
               .append("path")
               .attr("d", path)
               .style("fill", fillState);

            // Remove old data
            selection.exit().remove();

        });

    });

}





