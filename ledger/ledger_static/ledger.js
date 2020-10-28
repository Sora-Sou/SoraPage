//modal表单日期填充
function fill_date(mode, thisObj) {
    let year, month, date;
    if (mode == 'add') {
        const now = new Date();
        year = now.getFullYear();
        month = now.getMonth() + 1;
        date = now.getDate();
    } else if (mode == 'modify') {
        year = $(thisObj).parents('.day_card_collection').prevAll('.month_title').children('h3').text().split('年', 1);
        const day_date = $(thisObj).prevAll('.day_div').find('.day_date').text();
        month = day_date.split('月', 1);
        date = day_date.split('月', 2)[1].split('日', 1);
    }
    $('[name=year]').val(year);
    $('[name=month]').val(month);
    $('[name=date]').val(date);
}

function fill_sort_detail(sort) {
    const outcome_sort = ['早餐', '午餐', '晚餐', '夜宵', '零食', '饮料', '聚餐', '网购', '氪金', '其他'];
    const income_sort = ['生活费', '其他'];
    let type_arr;
    if (sort == "收入") {
        type_arr = income_sort;
    } else if (sort == '支出') {
        type_arr = outcome_sort;
    }
    $('[name=sort_detail]').empty();
    for (let i = 0; i < type_arr.length; i++) {
        let option = '<option>' + type_arr[i] + '</option>'
        $("[name='sort_detail']").append(option)
    }
}

//modal表单select关联修改
$(function () {
    fill_sort_detail($('[name=sort]').val());
    $('[name=sort]').change(function () {
        fill_sort_detail($('[name=sort]').val());
    })
})
//modal表单显示
$(function () {
    $('#add_icon').click(function () {
        $('.modal-title').text('添加记录');
        //初始化表单
        fill_sort_detail('支出');
        $('#modal_form input,#modal_form textarea').val('');
        //预设时间
        fill_date('add');
        const form_btn = `<button type="button" class="form-control btn btn-primary form_btn" id="add_btn">添加</button>`
        $('.form_btn').remove();
        $('#modal_form').append(form_btn);
        //智能填充支出类别
        const current_hour = new Date().getHours();
        if (current_hour > 7 && current_hour < 11) {
            $('[name=sort_detail]').val('早餐');
        } else if (current_hour >= 11 && current_hour < 16) {
            $('[name=sort_detail]').val('午餐');
        } else if (current_hour >= 16 && current_hour <= 20) {
            $('[name=sort_detail]').val('晚餐');
        } else if (current_hour > 20 || current_hour <= 6) {
            $('[name=sort_detail]').val('夜宵');
        }
        $('#modal').modal('show');
    })

    $('.outcome,.income').click(function () {
        fill_date('modify', this);
        const sort = $(this).attr('class');
        if (/outcome/.test(sort)) {
            $('[name=sort]').val('支出');
            fill_sort_detail('支出');
        } else {
            $('[name=sort]').val('收入');
            fill_sort_detail('收入');
        }
        $('[name=sort_detail]').val($(this).find('.sort_detail').text());
        const amount = $(this).find('.amount').text();
        const note = $(this).find('.note').text();
        $('[name=amount]').val(amount);
        $('[name=note]').val(note);
        $('.modal-title').text('修改记录');
        const form_btn = `<div class="form-row form_btn">
                              <div class="col"><button class="btn btn-danger w-100" type="button" id="delete_btn">删除</button></div>
                              <div class="col"><button class="btn btn-primary w-100" type="button" id="modify_btn">修改</button></div>
                          </div>`
        $('.form_btn').remove();
        $('#modal_form').append(form_btn);
        //后端传参id
        if ($('[name=data-id]').length == 0) {
            const id = $('<input type="hidden" name="data-id">').val($(this).attr('data-id'));
            $('#modal_form').append(id);
        } else {
            $('[name=data-id]').val($(this).attr('data-id'));
        }
        $('#modal').modal('show');
    })
})

//modal表单提交
$(function () {
    $('#modal_form').on('click', '#add_btn', function () {
        $.ajax({
            url: '/ledger/ajax/add',
            type: 'post',
            data: $('#modal_form').serialize(),
            success: function () {
                alert("添加成功");
                location.reload();
            }
        })
    })

    $('#modal_form').on('click', '#delete_btn', function () {
        $.ajax({
            url: '/ledger/ajax/delete',
            type: 'post',
            data: {'delete_id': $('[name=data-id]').val()},
            success: function () {
                alert("删除成功");
                location.reload();
            }
        })
    })

    $('#modal_form').on('click', '#modify_btn', function () {
        $.ajax({
            url: '/ledger/ajax/modify',
            type: 'post',
            data: $('#modal_form').serialize(),
            success: function () {
                alert("修改成功");
                location.reload();
            }
        })
    })
})
