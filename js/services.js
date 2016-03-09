var photos = null;
var planners = null;

if (typeof String.prototype.endsWith !== 'function') {
    String.prototype.endsWith = function(suffix) {
        return this.indexOf(suffix, this.length - suffix.length) !== -1;
    };
}

function svcGetPhotos(fn) {
    $.ajax({
        type: 'get',
        url: '/services/photos/',
        dataType: 'json',
        success: function (data) {
            photos = data;
            fn && fn(data);
        },
        error: function(jqXHR, textStatus, errorThrown){
            showError(textStatus);
        }
    });
}

function svcDeletePhoto(id, fn) {
    $.ajax({
        type: 'delete',
        url: '/services/photos/' + id,
        success: function (data) {
            showSuccess('Picture is deleted');
            setTimeout(function() {
                fn && fn();
            }, 500);
        },
        error: function(jqXHR, textStatus, errorThrown){
            showError(textStatus);
        }
    });
}

function svcGetPlanners(fn) {
    $.ajax({
        type: 'get',
        url: '/services/planners/',
        dataType: 'json',
        success: function (data) {
            planners = data;
            fn && fn();
        },
        error: function(jqXHR, textStatus, errorThrown){
            showError(textStatus);
        }
    });
}

function svcAddPlanner(data, fn) {
    $.ajax({
        type: 'post',
        url: '/services/planners/',
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            showSuccess('Planner is created');
            setTimeout(function() {
                fn && fn();
            }, 1000);
        },
        error: function(jqXHR, textStatus, errorThrown){
            showError(jqXHR.responseText);
        }
    });
}

function svcDeletePlanner(id, fn) {
    $.ajax({
        type: 'delete',
        url: '/services/planners/' + id,
        success: function (data) {
            showSuccess('Planner is deleted');
            setTimeout(function() {
                fn && fn();
            }, 500);
        },
        error: function(jqXHR, textStatus, errorThrown){
            showError(textStatus);
        }
    });
}