
var numValues = 100;
var maxFPS = 200.0;

var margin = {left: 30, right: 140, top: 8, bottom: 8, center: 16};
var width = 512;
var height = 64;

var data1 = Array.apply(null, new Array(numValues))
    .map(Number.prototype.valueOf, 0);
var data2 = Array.apply(null, new Array(numValues))
    .map(Number.prototype.valueOf, 0);

var x = d3.scale.linear()
    .domain([0, numValues - 1])
    .range([0, width - margin.left - margin.right]);
var y = d3.scale.linear()
    .domain([0.0, maxFPS])
    .range([height - margin.bottom, margin.top]);

var axis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .ticks(3)
    .innerTickSize(margin.left + margin.right - width)
    .outerTickSize(3);

var line = d3.svg.line()
    .x(function(d, i) { return x(i); })
    .y(function(d) { return y(d); });

var svg = d3.select("body")
    .append("svg")
        .attr("width", width)
        .attr("height", height);

var yAxis = svg.append("g")
    .attr("class", "axis")
    .attr("transform", "translate(" + 0.9 * margin.left + ", 0)")
    .call(axis);

var chart = svg.append("g")
    .attr("transform", "translate(" + margin.left + ", 0)");

var path1 = chart.append("path")
    .attr("id", "line1")
    .attr("class", "dataline")
    .attr("d", line(data1));

var path2 = chart.append("path")
    .attr("id", "line2")
    .attr("class", "dataline")
    .attr("d", line(data2));

var label1 = svg.append("text")
    .attr("id", "label1")
    .attr("class", "label")
    .attr("x", width - margin.right + 34)
    .attr("y", 0.5 * height)
    .style("font-size", Math.min(0.25 * height, 32))
    .text("rnd ");

var label2 = svg.append("text")
    .attr("id", "label2")
    .attr("class", "label")
    .attr("x", width - margin.right + 34)
    .attr("y", height - margin.bottom)
    .style("font-size", Math.min(0.25 * height, 32))
    .text("app ");

var num1 = svg.append("text")
    .attr("id", "num1")
    .attr("class", "numText")
    .attr("x", width - 10)
    .attr("y", 0.5 * height)
    .style("font-size", Math.min(0.45 * height, 64))
    .text("");

var num2 = svg.append("text")
    .attr("id", "num2")
    .attr("class", "numText")
    .attr("x", width - 10)
    .attr("y", height - margin.bottom)
    .style("font-size", Math.min(0.45 * height, 64))
    .text("");

function set_max_fps(fps) {
    maxFPS = fps;
    y.domain([0.0, maxFPS]);

    path1.attr("d", line(data1));
    path2.attr("d", line(data2));

    yAxis.call(axis);
}

function add_value_pair(firstValue, secondValue) {
    var value1 = parseFloat(firstValue)
    var value2 = parseFloat(secondValue)

    data1.shift();
    data1.push(value1);
    data2.shift();
    data2.push(value2);

    num1.text(d3.round(value1, 1));
    num2.text(d3.round(value2, 1));

    path1.attr("d", line(data1));
    path2.attr("d", line(data2));
}
