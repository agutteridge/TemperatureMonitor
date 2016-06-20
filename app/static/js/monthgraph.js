function httpGetAsync(theUrl, callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open("GET", theUrl, true); // true for asynchronous 
    xmlHttp.send(null);
};

httpGetAsync(document.baseURI + "/data", function(temp_data){
  var data = JSON.parse(temp_data);

  var mins_trace = {
    name: 'minimum',
    x: data.dates,
    y: data.mins,
    mode: 'markers+lines',
    marker: {
      color: 'rgb(0, 0, 255)',
      size: 4
    },
    line: {
      dash: 'dot',
      width: 2
    }
  };

  var maxs_trace = {
    name: 'maximum',
    x: data.dates,
    y: data.maxs,
    mode: 'markers+lines',
    marker: {
      color: 'rgb(255, 0, 0)',
      size: 4
    },
    line: {
      dash: 'dot',
      width: 2
    }
  };

  var means_trace = {
    name: 'mean',
    x: data.dates,
    y: data.means,
    mode: 'markers+lines',
    marker: {
      color: 'rgb(42, 142, 42)',
      size: 2
    }
  };

  data = [mins_trace, maxs_trace, means_trace]

  var layout = {
    showlegend: false,
    yaxis: {title: "Temperature (Celsius)",
            range: [-30, 30]},
    xaxis: {title: "Date",
            tickangle: 270},
    // autosize: false,
    width: 700,
    height: 450,
    margin: {
      l: 50,
      r: 50,
      b: 100,
      t: 10,
      pad: 4
    },
  };

  Plotly.newPlot(
    document.getElementById("monthgraph-canvas"),
    data,
    layout
  );
})