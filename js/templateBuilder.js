var templPlanner = '<li class="list-group-item clearfix">@@name@@' +
    '<span class="pull-right button-group">' +
    '<button type="button" class="btn btn-primary" onClick="editPlanner(\'@@key@@\', \'@@squotename@@\')"><span class="glyphicon glyphicon-edit"></span> Edit</button> ' +
    '<button type="button" class="btn btn-danger" onClick="delPlanner(this, \'@@key@@\');"><span class="glyphicon glyphicon-remove"></span> Delete</button>' +
    '</span>' +
    '<p class="list-group-item-text">@@description@@</p>' + 
    '<p class="list-group-item-text">@@creationdate@@</p>' +
    '</li>';

var templPhoto = '<div class="col-xs-8 col-sm-6 col-md-4">' +            
    '<div class="thumbnail">' +
    '<div class="caption">' +                    
    '<p><a href="javascript:delPhoto(this, \'@@key@@\')" class="label label-danger">Remove</a><p>' +
    '<p>@@name@@</p>' +
    '<p>(@@creationdate@@)</p>' +
    '</div><img src="/services/photo/@@key@@" alt="@@name@@"></div>' +
    '</div>';

var templPhotoSel = '<div class="col-xs-8 col-sm-6 col-md-4">' +            
    '<div class="thumbnail">' +
    '<div class="caption">' +                    
    '<p><a href="javascript:selectPhoto(\'@@key@@\')" class="label label-danger">Select</a><p>' +
    '<p>@@name@@</p>' +
    '</div><img src="/services/photo/@@key@@" alt="@@name@@"></div>' +
    '</div>';

var currentPlanner = null;

function getPlannersHtml() {
	var html = planners.map(function(x) {
		var d = new Date(x.creationdate + ' UTC');
		var squotename = x.name.replace(/'/g, '&amp;#39;');
		return templPlanner.replace(
			/@@name@@/g, x.name).replace(
			/@@squotename@@/g, squotename).replace(
			/@@key@@/g, x.key).replace(
			/@@description@@/g, x.description).replace(
			/@@creationdate@@/g, moment(d).format("dddd YYYY-MM-DD hh:mm a"));
	}).join(' ');
	return html || '<p>You do not have any planners. </p>';
}

function tagswapPhoto(str, x) {
	var d = new Date(x.creationdate + ' UTC');
	return str.replace(
		/@@name@@/g, x.name).replace(
		/@@key@@/g, x.key).replace(
		/@@contenttype@@/g, x.contenttype).replace(
		/@@creationdate@@/g, moment(d).format("YYYY-MM-DD hh:mm a"));	
}

function getPhotosHtml() {
	var html = photos.map(function(x) {
		return tagswapPhoto(templPhoto, x);
	}).join(' ');
	return html || '<p>You do not have any pictures. </p>';	
}

function getSelectPhotosHtml() {
	var html = photos.map(function(x) {
		return tagswapPhoto(templPhotoSel, x);
	}).join(' ');
	return html || '<p>You do not have any pictures. </p>';	
}

function editPlanner(key, name) {
	currentPlanner = key;
	$('#dlgEditPlanner').modal('show');
	$('#headerEditPlanner').html(name);
}