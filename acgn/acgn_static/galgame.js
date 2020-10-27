const galgame_detail = [{
    "id": 1,
    "name": "金色loveriche",
    "target": "characterRank",
    "content": {
        "rank": [
            {
                "rank": "S-",
                "comment": "",
                "character": "公主"
            },
            {
                "rank": "A+",
                "comment": "",
                "character": "玲奈"
            }],
        "comment": "123"
    }
}]

//avoid character '+' in CSS selector
const overall_class = {
    'S': 'S',
    'S-': 'S_minus',
    'A+': 'A_plus',
    'A': 'A',
    'A-': 'A_minus',
    'B': 'B'
}

const rank_visualize_progress = {
    'S': '100%',
    'S-': '90%',
    'A+': '80%',
    'A': '70%',
    'A-': '60%',
    'B': '50%'
}

const rank_visualize_rank = {
    'S': 5,
    'S-': 4.5,
    'A+': 4,
    'A': 3.5,
    'A-': 3,
    'B': 2.5
}


function ul_obj_convert(galgame_obj) {
    const value_order = ['overall', 'plot', 'characterRank', 'music', 'CG'];
    const aspect = ['综评', '剧情', '人设', '音乐', '画风'];
    const rank = [];
    for (let i = 0; i < value_order.length; i++) {
        rank.push(galgame_obj[value_order[i]]);
    }
    return {'value': value_order, 'aspect': aspect, 'rank': rank};
}

function render_card(galgame_obj) {
    let card = $('<div></div>').addClass('card rank_' + overall_class[galgame_obj['overall']]).addClass('mt-4 mt-md-0');
    // carousel
    let carousel = $('<div></div>').addClass('carousel slide').attr('data-ride', 'carousel').attr('id', galgame_obj['name']);
    let carousel_inner = $('<div></div>').addClass('carousel-inner rounded-top');
    for (let i = 0; i < galgame_obj['imgLen']; i++) {
        let carousel_item = $('<div></div>').addClass('carousel-item');
        if (i === 0) {
            carousel_item.addClass('active');
        }
        let img = $('<img>').attr('src', '/acgn/acgn_static/galgame/' + galgame_obj['name'] + '_' + (i + 1) + '.png');
        carousel_item.append(img);
        carousel_inner.append(carousel_item);
    }
    carousel.append(carousel_inner);
    carousel.append('<a class="carousel-control-prev" href="#' + galgame_obj['name'] + '" data-slide="prev"><span class="carousel-control-prev-icon"></span></a>');
    carousel.append('<a class="carousel-control-next" href="#' + galgame_obj['name'] + '" data-slide="next"><span class="carousel-control-next-icon"></span></a>');
    // h3
    const h3 = $('<h3></h3>').addClass('text-center p-3').text(galgame_obj['name']);
    // ul
    const ul_obj = ul_obj_convert(galgame_obj);
    let ul = $('<ul></ul>').addClass('list-group list-group-flush');
    for (let i = 0; i < ul_obj['aspect'].length; i++) {
        let li = $('<li></li>').addClass('list-group-item').attr('id', galgame_obj['name'] + '_' + ul_obj['value'][i]);
        //list_flex
        let list_flex = $('<div class="list_flex"></div>')
        //span
        const span_text = ul_obj['aspect'][i] + ': ' + ul_obj['rank'][i];
        let span = $('<span></span>').addClass('list_flex_text').text(span_text);
        //progress
        let progress = $('<div></div>').addClass('progress list_flex_progress');
        progress.append($('<div></div>').addClass('progress-bar progress-bar-striped progress-bar-animated').css('width', rank_visualize_progress[ul_obj['rank'][i]]));
        //append
        list_flex.append(span, progress);
        li.append(list_flex);
        ul.append(li);
    }
    //card append
    card.append(carousel, h3, ul);
    return card;
}

function render_detail(detail_obj) {
    const target = detail_obj['name'] + '_' + detail_obj['target'];
    const detail_collapse_id = target + '_' + 'collapse';

    function add_collapse_toggler() {
        const toggler = $('<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" class="detail_toggler ml-3"><path d="M454.188 785.022c-145.192-150.177-290.378-300.353-435.422-450.526-59.842-61.836 37.327-154.021 97.313-91.899 129.23 133.647 258.318 267.296 387.548 400.868 133.646-134.287 267.436-268.574 401.083-402.934 60.84-61.123 158.011 31.060 97.244 91.971-150.105 150.89-300.279 301.703-450.454 452.521-24.933 24.934-72.666 25.575-97.311 0z"></path></svg>')
        $('#' + target).attr({'data-toggle': 'collapse', 'data-target': '#' + detail_collapse_id})
        $('#' + target).find('.list_flex').append(toggler)
    }

    if (detail_obj['content']['rank']) {
        add_collapse_toggler()
        let nest_ul = $('<ul class="list-group list-group-flush collapse detail_collapse" id="' + detail_collapse_id + '"></ul>');
        for (let i = 0; i < detail_obj['content']['rank'].length; i++) {
            // this_rank sample
            // {
            //     "rank": "S-",
            //     "comment": "",
            //     "character": "公主"
            // }
            const this_rank = detail_obj['content']['rank'][i];
            //li
            let nest_li = $('<li class="list-group-item"></li>');

            let list_flex = $('<div class="list_flex"></div>');
            //list_flex span
            const span_text = this_rank['character'] + ': ' + this_rank['rank'];
            const span = $('<span class="list_flex_text"></span>').text(span_text)
            let rank = $('<div class="list_flex_rank"></div>')
            for (let k = 0; k < Math.floor(rank_visualize_rank[this_rank['rank']]); k++) {
                if (detail_obj['target'] == 'characterRank') {
                    rank.append($('<img src="/acgn/acgn_static/heart.svg" class="heart ml-2">'));
                } else {
                    rank.append($('<img src="/acgn/acgn_static/star.svg" class="star ml-2">'));
                }
            }
            if (rank_visualize_rank[this_rank['rank']] * 2 % 2 == 1) {
                if (detail_obj['target'] == 'characterRank') {
                    rank.append($('<img src="/acgn/acgn_static/heart.svg" class="heart ml-2">'));
                } else {
                    rank.append($('<img src="/acgn/acgn_static/half_star.svg" class="star ml-2">'));
                }
            }
            //append
            list_flex.append(span, rank);
            nest_li.append(list_flex);

            if (this_rank['comment']) {
                nest_li.append($('<p class="pt-2 m-0"></p>').text(this_rank['comment']))
            }
            nest_ul.append(nest_li)
        }

        if (detail_obj['content']['comment'] != '') {
            nest_ul.append($('<li class="list-group-item"></li>').text(detail_obj['content']['comment']))
        }

        //render
        $('#' + target).append(nest_ul)
    } else if (detail_obj['content']['comment'] != '') {
        add_collapse_toggler()
        $('#' + target).append($('<div class="collapse mt-2 ml-4 detail_collapse" id="' + detail_collapse_id + '"></div>').text(detail_obj['content']['comment']))
    }
}

function no_toggler_css() {
    $('.progress').each(function () {
        if ($(this).next('svg').length == 0) {
            $(this).css('margin-right', '32px')
        }
    })
}

function toggler_animation() {
    $('.detail_collapse').on('show.bs.collapse', function () {
        $(this).prev().find('svg').addClass('detail_toggler_onshow').removeClass('detail_toggler_onhide')
    })
    $('.detail_collapse').on('hide.bs.collapse', function () {
        $(this).prev().find('svg').addClass('detail_toggler_onhide').removeClass('detail_toggler_onshow')
    })
}

function detail_off() {

}

function ajax_card(json_data) {
    let counter = 0;
    for (let i = 0; i < json_data.length; i++) {
        if (counter % 2 == 0) {
            $('#card_container').append($('<div class="row"></div>'));
        }
        counter++;
        let col = $('<div class="col-md-6"></div>');
        col.append(render_card(json_data[i]));
        $('#card_container').find('.row').last().append(col);
    }
    current_card += json_data.length;
}

let current_card = 0;

$(document).ready(function () {
    //render_card
    $.ajax({
        url: '/acgn/galgame/ajax/card',
        data: 'offset=' + current_card,
        dataType: 'json',
        success: function (data) {
            ajax_card(data);
        }
    })
    //render_detail
    $.ajax({
        url: '/acgn/galgame/ajax/detail',
        dataType: 'json',
        success: function (data) {
            for (let i = 0; i < data.length; i++) {
                //python的jsonify将原本为对象的data[i]['content']转换为了字符串
                data[i]['content'] = JSON.parse(data[i]['content']);
                render_detail(data[i]);
            }
            no_toggler_css()
            toggler_animation()
        }
    })
})