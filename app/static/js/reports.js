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
		document.location.href = document.baseURI + "/" + year + "-" + month;
	} else {
                message = document.getElementById("message").innerHTML = "Please select a year and month!"

        };
};
