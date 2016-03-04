var templPlanner = '<li class="list-group-item clearfix">@@name@@' +
    '<span class="pull-right button-group">' +
    '<button type="button" class="btn btn-primary"><span class="glyphicon glyphicon-edit"></span> Edit</button> ' +
    '<button type="button" class="btn btn-danger" onClick="delPlanner(this, \'@@key@@\');"><span class="glyphicon glyphicon-remove"></span> Delete</button>' +
    '</span>' +
    '<p class="list-group-item-text">@@description@@</p>' + 
    '<p class="list-group-item-text">@@creationdate@@</p>' +
    '</li>';

var planners = [];

function addPlanner(key, creator, name, description, creationdate) {
	var date = new Date(creationdate + ' UTC');
	planners.push({
		key: key,
		creator: creator,
		name: name,
		description: description,
		creationdate: date.toString()
	});	
}

function insertPlanners() {
	var html = planners.map(function(x) {
		var d = new Date(x.creationdate + ' UTC');
		return templPlanner.replace(
			'@@name@@', x.name).replace(
			'@@key@@', x.key).replace(
			'@@description@@', x.description).replace(
			'@@creationdate@@', d.toString());
	}).join(' ');
	$('#listPlanners').html(html);
}