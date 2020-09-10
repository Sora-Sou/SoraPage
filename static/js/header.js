$(document).ready(function () {
    $(".nav-link").mouseenter(function () {
        $(this).css('color', '#fd7e14');
        $(this).children(".nav_header_svg").css('fill', '#fd7e14');
    })
    $(".nav-link").mouseleave(function () {
        $(this).css('color', 'rgb(0, 191, 255)');
        $(this).children(".nav_header_svg").css('fill', 'rgb(0, 191, 255)');
    })

    $('#navbar_header_collapse').on('show.bs.collapse', function () {
        $('#navbar_header_toggler').addClass('navbar_header_toggler_showing').removeClass('navbar_header_toggler_hiding')
    })
    $('#navbar_header_collapse').on('hide.bs.collapse', function () {
        $('#navbar_header_toggler').addClass('navbar_header_toggler_hiding').removeClass('navbar_header_toggler_showing')
    })

    const navbar_header_height = $('#navbar_header').outerHeight(true)
    $('#navbar_header').next().css('margin-top', navbar_header_height)
})
