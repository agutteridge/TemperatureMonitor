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
