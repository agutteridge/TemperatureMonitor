// ALL PAGES
// Opening and closing the sidebar menu
function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
}

function httpGetAsync(theUrl, callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open("GET", theUrl, true); // true for asynchronous 
    xmlHttp.send(null);
};

// INDEX
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
      layout
    );
  }
})

// REPORTS
var btn_submit = document.getElementById("btn_submit");

btn_submit.onclick = function(){
  var yeardropdown = document.getElementById("year-dropdown");
  var monthdropdown = document.getElementById("month-dropdown");
  var year = yeardropdown.options[yeardropdown.selectedIndex].text;
  var month = monthdropdown.options[monthdropdown.selectedIndex].text;
  if (year != "Year" && month != "Month") {
    switch(month) {
        case "January":
            month = "01"
            break;
        case "February":
            month = "02"
            break;
        case "March":
            month = "03"
            break;
        case "April":
            month = "04"
            break;
        case "May":
            month = "05"
            break;
        case "June":
            month = "06"
            break;
        case "July":
            month = "07"
            break;
        case "August":
            month = "08"
            break;
        case "September":
            month = "09"
            break;
        case "October":
            month = "10"
            break;
        case "November":
            month = "11"
            break;
        case "December":
            month = "12"
            break;
    }
    console.log('hello?')
    document.location.href = document.baseURI + "/" + year + "-" + month;
  } else {
    message = document.getElementById("message").innerHTML = "Please select a year and month!"
  };
};

// MONTH GRAPH
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
