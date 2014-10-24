// Counts occurences of each element in an array
function count_occurences(data_array) {
    occurences = [];
    $.each(data_array, function(i, item) {
        var count = $.grep(data_array, function(elem) {
            return elem == item;
        }).length;
        if (item == "") {
            occurences.push({'label': "(Leer)", 'value': count});
        } else {
            occurences.push({'label': item, 'value': count});
        }
    });

    return [{'key': 'Cumulative Return', 'values': occurences}]
}


//nvd3: Regular pie chart example
function addPieChart(items, container) {
  nv.addGraph(function() {
    var svg_container = container + " svg";
    var width = $(container).parent().width();
    
    var svg_container = container + " svg";

    var svg = d3.select(container).append("svg")
        .attr("width", width)
        .attr("height", 500);

    var chart = nv.models.pieChart()
        .x(function(d) { return d.label })
        .y(function(d) { return d.value })
        .showLabels(true);

    d3.select(svg_container)
        .datum(items)
        .transition().duration(350)
        .call(chart);

    nv.utils.windowResize(chart.update);
    return chart;
  });
}

// nvd3: Discrete bar chart
function addDiscreteChart(items, container) {
    nv.addGraph(function() {
      var svg_container = container + " svg";
      var width = $(container).parent().width();

      var svg = d3.select(container).append("svg")
        .attr("width", width)
        .attr("height", 500);  

      var chart = nv.models.discreteBarChart()
          .x(function(d) { return d.label })    //Specify the data accessors.
          .y(function(d) { return d.value })
          .staggerLabels(true)    //Too many bars and not enough room? Try staggering labels.
          .tooltips(true)         //Don't show tooltips
          .showValues(true)       //...instead, show the bar value right on top of each bar.
          .transitionDuration(350);

      d3.select(svg_container)
          .datum(items)
          .call(chart);

      nv.utils.windowResize(chart.update);
      return chart;
    });
}