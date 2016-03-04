var templPlanner = '<li class="list-group-item clearfix">@@name@@' +
    '<span class="pull-right button-group">' +
    '<button type="button" class="btn btn-primary"><span class="glyphicon glyphicon-edit"></span> Edit</button> ' +
    '<button type="button" class="btn btn-danger" onClick="delPlanner(this, \'@@key@@\');"><span class="glyphicon glyphicon-remove"></span> Delete</button>' +
    '</span>' +
    '<p class="list-group-item-text">@@description@@</p>' + 
    '<p class="list-group-item-text">@@creationdate@@</p>' +
    '</li>';

var templPhoto = '<li class="list-group-item clearfix">@@name@@' +
    '<span class="pull-right button-group">' +
    '<button type="button" class="btn btn-primary"><span class="glyphicon glyphicon-edit"></span> Edit</button> ' +
    '<button type="button" class="btn btn-danger" onClick="delPhoto(this, \'@@key@@\');"><span class="glyphicon glyphicon-remove"></span> Delete</button>' +
    '</span>' +
    '<p class="list-group-item-text">@@contenttype@@</p>' + 
    '<p class="list-group-item-text">@@creationdate@@</p>' +
    '</li>';

var planners = null;
var photos = null;

function addPlanners(data) {
	planners = data;
	var html = planners.map(function(x) {
		var d = new Date(x.creationdate + ' UTC');
		return templPlanner.replace(
			'@@name@@', x.name).replace(
			'@@key@@', x.key).replace(
			'@@description@@', x.description).replace(
			'@@creationdate@@', d.toString());
	}).join(' ');
	html = html || '<p>You do not have any planners. </p>';
	$('#listPlanners').html(html);
}

function addPhotos(data) {
	photos = data;
	var html = photos.map(function(x) {
		var d = new Date(x.creationdate + ' UTC');
		return templPhoto.replace(
			'@@name@@', x.name).replace(
			'@@key@@', x.key).replace(
			'@@contenttype@@', x.contenttype).replace(
			'@@creationdate@@', d.toString());
	}).join(' ');
	html = html || '<p>You do not have any pictures. </p>';	
	$('#listPhotos').html(html);
}