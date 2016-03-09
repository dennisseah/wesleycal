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

$(".nav a").on("click", function(){
    $(".nav").find(".active").removeClass("active");
    $(this).parent().addClass("active");
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
