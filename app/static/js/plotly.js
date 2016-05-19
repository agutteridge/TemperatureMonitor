function httpGetAsync(theUrl, callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open("GET", theUrl, true); // true for asynchronous 
    xmlHttp.send(null);
};

httpGetAsync(document.baseURI + "daygraph", function(temp_data){
  data = [JSON.parse(temp_data)];

  // empty dict is returned if no readings in last 24 hours
  if (data[0].x[0] != null) {
    now = new Date().getTime();
    oneDayAgo = now - 86400000; // 24hrs in ms

    var layout = {
      showlegend: false,
      yaxis: {title: "Temperature (Celsius)",
              range: [-30, 30]},
      xaxis: {title: "Time",
              range: [oneDayAgo, now],
              tickangle: 0,
              dtick: 86400000 / 6},
      autosize: false,
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

    Plotly.plot(
      document.getElementById("graph-canvas"),
      data,
      layout,
      {staticPlot: true}
    );
  }
})

readTimeInMs = data.date.getTime()
readTimeInSeconds = readTimeInMs % 60
readTimeInMins = Math.floor(readTimeInMs / 60)
timeAgo = ""
if (readTimeInMins > 0) {
  timeAgo += str(readTimeInMins) += " minutes and "
}
timeAgo += str(readTimeInSeconds) += " seconds ago"
