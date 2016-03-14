
fetchPlanners();
fetchPhotos();
selectNav();


// =========
function todayDate() {
    var d = new Date();
    var m = d.getMonth() +1;
    m = (m < 10) ? '0' + m : '' + m;
    var dy = d.getDate();
    dy = (dy < 10) ? '0' + dy : '' + dy;

    return d.getFullYear() + m + dy;
}

var currentDay = todayDate();

function getDisplayDate(d) {
	d = '' + d;
	var year = parseInt(d.substring(0, 4));
	var month = parseInt(d.substring(4, 6)) -1;
	var date = parseInt(d.substring(6));
	var m = moment(new Date(year, month, date));
	return m.format('dddd') + ' | ' + m.format('LL') + ' | Week ' + m.format('W') ;
}