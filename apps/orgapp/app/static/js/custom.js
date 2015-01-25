global_height = 600;

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

// Returns selected options from multiselects
function get_multiselect(container) {
    var options = [];
    $(container + ' option:selected').each(function () {
        options.push($(this).text());
    });
    return options;
}

// The same just using an object rather than a container
function get_multiselect_by_obj(obj) {
    var options = [];
    $('option:selected', obj).each(function () {
        options.push($(this).text());
    });
    return options;
}

//nvd3: Regular pie chart example
function nvd3_pie_chart(items, container) {
  nv.addGraph(function() {
    var svg_container = container + " svg";
    var width = $(container).parent().width();

    var svg_container = container + " svg";

    var svg = d3.select(container).append("svg")
        .attr("width", width)
        .attr("height", global_height);

    var chart = nv.models.pieChart()
        .x(function(d) { return d.label })
        .y(function(d) { return d.value })
        .showLabels(true);

    // Show value
    chart.pie.pieLabelsOutside(false).labelType("percent");

    // Add colors
    var colors = [];
    for (x in items) {
      colors.push(items[x].color)
    }

    chart.color(colors);

    d3.select(svg_container)
        .datum(items)
        .transition().duration(350)
        .call(chart);

    nv.utils.windowResize(chart.update);
    return chart;
  });
}

// nvd3: Discrete bar chart
function nvd3_discrete_chart(items, container) {
    nv.addGraph(function() {
      var svg_container = container + " svg";
      var width = $(container).parent().width();

      var svg = d3.select(container).append("svg")
        .attr("width", width)
        .attr("height", global_height);

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

// dimpleJS: Add new horizontal bar
function dimplejs_horizontal_bar (data, container) {
    var svg_container = container + " svg";
    var width = $(container).parent().width();

    var svg = d3.select(container).append("svg")
    .attr("width", width)
    .attr("height", global_height);

    var myChart = new dimple.chart(svg, data);
    myChart.setBounds(200, 30, width-250, global_height-70);
    x = myChart.addMeasureAxis("x", "value");
    y = myChart.addCategoryAxis("y", "label");
    y.addOrderRule("label", true);
    series = myChart.addSeries("label", dimple.plot.bar);
    myChart.draw();
}

// dimpleJS: Add new horizontal stacked grouped bar
function dimplejs_horiz_stacked_grouped_bar(data, container){
    var svg_container = container + " svg";
    var width = $(container).parent().width();

    var svg = d3.select(container).append("svg")
    .attr("width", width)
    .attr("height", global_height);

    var myChart = new dimple.chart(svg, data);
    myChart.setBounds(200, 30, width-250, global_height-70);
    myChart.addMeasureAxis("x", "value");
    var y = myChart.addCategoryAxis("y", ["group", "label"]);
    y.addOrderRule("label", true);
    var s = myChart.addSeries("label", dimple.plot.bar);
    myChart.addLegend(60, 10, width-60, 20, "center");

    // Add extra modifications
    s.afterDraw = function (shape, data) {
        // Get the shape as a d3 selection
        var s = d3.select(shape),
        rect = {
            x: parseFloat(s.attr("x")),
            y: parseFloat(s.attr("y")),
            width: parseFloat(s.attr("width")),
            height: parseFloat(s.attr("height"))
        };
        // Only label bars where the text can fit
        if (rect.height >= 8) {
            // Add a text label for the value
            svg.append("text")
                // Position in the centre of the shape (vertical position is
                // manually set due to cross-browser problems with baseline)
                .attr("x", rect.x + rect.width / 2)
                .attr("y", rect.y + rect.height / 2 + 3.5)
                // Centre align
                .style("text-anchor", "middle")
                .style("font-size", "10px")
                .style("font-family", "sans-serif")
                // Make it a little transparent to tone down the black
                .style("opacity", 0.6)
                // Format the number
                .text(d3.format("s")(data.xValue));
        }
    };
    myChart.draw();
}

// Filter global
function fnFilterGlobal (dt_table) {
    $(dt_table).dataTable().fnFilter(
        $("#global_filter").val(),
        null,
        $("#global_regex")[0].checked,
        $("#global_smart")[0].checked
    );
}

// Filter by certain columns
function fnFilterColumn (dt_table, i) {
    $(dt_table).dataTable().fnFilter(
        $("#col"+(i)+"_filter").val(),
        i,
        $("#col"+(i)+"_regex")[0].checked,
        $("#col"+(i)+"_smart")[0].checked
    );
}
