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
  var layout = {
    title: "The last 24 hours",
    showlegend: false
  };

  console.log(data.y);

  Plotly.plot(
    document.getElementById("graph-canvas"),
    data,
    layout,
    {staticPlot: true}
  );
})
