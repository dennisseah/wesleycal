function hideAllViews() {
    $('#homeview').hide();
    $('#plannerView').hide();
    $('#photoView').hide();
}

function addLocationTag(tag) {
    var loc = location.href;
    var idx = loc.lastIndexOf('#');
    if (idx !== -1) {
        loc = loc.substring(0, idx);
    }
    location.href = loc + '#' + tag;
}

function showHomeView() {
    hideAllViews();
    $('#homeview').show();
    addLocationTag('home');
}

function showPlannerView() {
    hideAllViews();
    $('#plannerView').show();
    addLocationTag('planner');
}

function showPhotoView() {
    hideAllViews();
    $('#photoView').show();
    addLocationTag('photo');
}


function alertShow(oAlert, message, t) {
	t = t || 2000;
	oAlert.find('#message').html(message);
	oAlert.show();
	oAlert.fadeTo(t, 500).slideUp(500, function(){
    	oAlert.hide();
	});
}

function showError(message) {
	alertShow($('#alertError'), message, 5000);
}

function showSuccess(message) {
	alertShow($('#alertSuccess'), message);
}

function fetchPlanners(force) {
    if (!force && planners) {
        return;
    }
    $.ajax({
        type: 'get',
        url: '/services/planners/',
        dataType: 'json',
        success: function (data) {
            addPlanners(data);
        },
        error: function(jqXHR, textStatus, errorThrown){
            showError(textStatus);
        }
    });    
}

function fetchPhotos(force) {
    if (!force && photos) {
        return;
    }
    $.ajax({
        type: 'get',
        url: '/services/photos/',
        dataType: 'json',
        success: function (data) {
            addPhotos(data);
        },
        error: function(jqXHR, textStatus, errorThrown){
            showError(textStatus);
        }
    });    
}

function delPlanner(oBtn, id) {
    $(oBtn).prop('disabled', true);
    $.ajax({
        type: 'delete',
        url: '/services/planners/' + id,
        success: function (data) {
            showSuccess('Planner is deleted');
            setTimeout(function() {
                fetchPlanners(true);    
            }, 500);
        },
        error: function(jqXHR, textStatus, errorThrown){
            showError(textStatus);
        }
    });
}

function delPhoto(oBtn, id) {
    $(oBtn).prop('disabled', true);
    $.ajax({
        type: 'delete',
        url: '/services/photos/' + id,
        success: function (data) {
            showSuccess('Picture is deleted');
            setTimeout(function() {
                fetchPhotos(true);    
            }, 500);
        },
        error: function(jqXHR, textStatus, errorThrown){
            showError(textStatus);
        }
    });
}


$(".nav a").on("click", function(){
    $(".nav").find(".active").removeClass("active");
    $(this).parent().addClass("active");
});

$("#fileinput").fileinput({
    uploadUrl: '/services/photos/',
    uploadAsync: true,
    allowedFileExtensions: ['png', 'jpg','jpeg'],
    maxFileSize: 2500,
	maxFileCount: 1
});

$("#fileinput").on('fileuploaded', function() {
    fetchPhotos(true);
    setTimeout(function() {
        $('#fileinput').fileinput('clear');
    }, 1000);
});

$('#btnOpenDlgPhoto').on('click', function() {
	$('#dlgPhotos').modal('show');
});


$('#btnOpenDlgCreatePlanner').on('click', function() {
	$('#newPlannerName').val('');
	$('#newPlannerDescription').val('');
	$('#btnCreatePlanner').prop('disabled', true);
	$('#dlgCreatePlanner').modal('show');
	setTimeout(function() {
		$('#newPlannerName').focus();	
	}, 1000);
});

$('#btnCreatePlanner').on('click', function() {
	var data = {
		name: $('#newPlannerName').val(),
		description: $('#newPlannerDescription').val()
	};
	
    $.ajax({
        type: 'post',
        url: '/services/planners/',
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        success: function (data) {
        	showSuccess('Planner is created');
            setTimeout(function() {
                fetchPlanners(true);    
            }, 1000);
        },
        error: function(jqXHR, textStatus, errorThrown){
        	showError(jqXHR.responseText);
        }
    });
	$('#dlgCreatePlanner').modal('hide');
});

$('#newPlannerName').on('keyup blur',function() {
	var disable = ($(this).val().trim()) ? false : true;
	$('#btnCreatePlanner').prop('disabled', disable);
});

function selectNav() {
    var possible = ['home'];
    if ($('#navPlanner').length) {
        possible.push('planner');
    }
    if ($('#navPhoto').length) {
        possible.push('photo');
    }

    var loc = location.href;
    var nav = 'home';
    var idx = loc.lastIndexOf('#');

    if (idx !== -1) {
        nav = loc.substring(idx+1).toLowerCase();
        loc = loc.substring(0, idx);
    }

    if (possible.indexOf(nav) === -1) {
        location.href = loc;
    }

    if (nav == 'home') {
        showHomeView();
        $('#navHome').addClass('active');
    } else if (nav == 'planner') {
        showPlannerView();
        $('#navPlanner').addClass('active');
    } else if (nav == 'photo') {
        showPhotoView();
        $('#navPhoto').addClass('active');
    }

}

fetchPlanners();
fetchPhotos();
selectNav();