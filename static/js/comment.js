function media(comment_obj) {
    var media = $('<div></div>').addClass('media');
    var avatar = $('<img>').attr({src: '/static/img/avatar.png', width: '64px'})
    var media_body = $('<div></div>').addClass('media-body').attr('data-comment-id', comment_obj['id'])


    var media_bar_1 = $('<div></div>').addClass('media_bar')
    media_bar_1.append($('<h5></h5>').text(comment_obj['name']).addClass('mb-0'))
    media_bar_1.append($('<p></p>').text('#' + comment_obj['sequence']).addClass(['text-muted', 'comment_sequence']))

    var media_bar_2 = $('<div></div>').addClass('media_bar')
    media_bar_2.append($('<small></small>').addClass('text-muted').text(comment_obj['time']))
    media_bar_2.append($('<button></button>').addClass(['btn', 'btn-link', 'btn_reply']).text('回复'))

    media_body.append(media_bar_1, media_bar_2)
    if (comment_obj['replyTo']) {
        media_body.append($('<span></span>').text('回复#' + comment_obj['replyToSeq'] + ": ").addClass('text-success'))
    }
    media_body.append($('<span></span>').text(comment_obj['comment']).addClass('comment_content'))

    media.append(avatar, media_body)
    return media
}

function render(comment_json) {
    if (comment_json['parent'].length == 0) {
        const no_comment = $('<p></p>').text('≧﹏≦ 当前页面没有评论呢').addClass('text-muted').attr('id', 'no_comment')
        $('#comment_container').append(no_comment)
        $('#comment_container').css({
            'display': 'flex',
            'justify-content': 'center'
        })
    } else {
        for (var i = 0; i < comment_json['parent'].length; i++) {
            $('#comment_container').append(media(comment_json['parent'][i]))

            if (i != comment_json['parent'].length - 1) {
                $('#comment_container').append($('<hr>'))
            }
        }

        for (var i = 0; i < comment_json['child'].length; i++) {
            var judge = "[data-comment-id='" + comment_json['child'][i]['parent'] + "']"
            $(judge).append($('<hr>'), media(comment_json['child'][i]))
        }
    }
    //判断登录状态
    if (comment_json['login_user']) {
        $('#comment_name').val(comment_json['login_user']['name'])
        $('#comment_email').val(comment_json['login_user']['email'])
    }
}

function load() {
    $.ajax({
        url: '/comment',
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            render(data)
        }
    })
}


function reload(comment_json) {
    $('#comment_container').empty().removeAttr('style')
    render(comment_json)
}

function now() {
    var time = new Date();
    var now = new String();
    now += time.getFullYear() + "-" + (time.getMonth() + 1) + "-" + time.getDate() + " ";
    now += time.getHours() + ":" + time.getMinutes() + ":" + time.getSeconds();
    return now
}

window.onload = function () {
    load()
    //回复功能
    $('#comment_container').on('click', '.btn_reply', function () {
        const comment_sequence = $(this).parent().prev().find('.comment_sequence').text()
        const comment_author = $(this).parent().prev().find('h5').text()
        const comment_content = $(this).parent().nextAll('.comment_content').text()
        $('#comment_sequence').text(comment_sequence)
        $('#comment_author').text(comment_author)
        $('#comment_content').text(comment_content)
        $('#reply_inform').fadeIn()
        const replyTo = $(this).parents('.media-body').first().attr('data-comment-id')
        const replyToSeq = $(this).parent().prev().find('.comment_sequence').text().slice(1)
        parent = $(this).parents('.media-body').last().attr('data-comment-id')
        $('#comment_parent').val(parent)
        $('#comment_replyTo').val(replyTo)
        $('#comment_replyToSeq').val(replyToSeq)
    })

    $('#btn_cancel_reply').click(function () {
        $('#reply_inform').fadeOut()
        $('#comment_parent').val('')
        $('#comment_replyTo').val('')
        $('#comment_replyToSeq').val('')
    })
    //评论验证与AJAX
    $('#submit_comment').click(function () {
        var validation = true
        $('.comment_input').each(function () {
            if ($(this).val() == '') {
                validation = false
                $(this).removeClass('valid_input').addClass('invalid_input')
            } else {
                $(this).removeClass('invalid_input').addClass('valid_input')
            }
            if (!validation) {
                $('#fail_comment_cause').text('昵称和邮箱是不是忘填了？')
                $('#fail_comment').modal('show')
            }
        })
        if ($('#comment_textarea').val() == '') {
            validation = false
            $('#fail_comment_cause').text('空空的评论区，认真的嘛？')
            $('#fail_comment').modal('show')
        }
        //AJAX
        if (validation) {
            $('.comment_input').each(function () {
                $(this).removeClass('valid_input invalid_input')
            })
            $('#comment_time').val(now())
            $.ajax({
                url: '/comment',
                data: $('#comment_form').serialize(),
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                    reload(data)
                }
            })
        }
    })
}