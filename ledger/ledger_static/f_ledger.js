const data_sample = [
    {
        "amount": "123",
        "auditor": "\u4f0d\u5cb3\u658c",
        "cashier": "\u4f0d\u5cb3\u658c",
        "first_hand": "\u4f0d\u5cb3\u658c",
        "id": 1,
        "item": "123",
        "remark": "123",
        "sort": "\u652f\u51fa",
        "insert_time": "2020-07-30"
    },
    {
        "amount": "123",
        "auditor": "\u4f0d\u5cb3\u658c",
        "cashier": "\u4f0d\u5cb3\u658c",
        "first_hand": "\u4f0d\u5cb3\u658c",
        "id": 1,
        "item": "123",
        "remark": "123",
        "sort": "\u652f\u51fa",
        "insert_time": "2020-07-30"
    }
]

//sum总金额 num交易笔数
let out_sum = 0;
let out_num = 0;
let in_sum = 0;
let in_num = 0;
let count_year = {}

function title_month_overall_calc(data, year) {
    for (let i = 0; i < data.length; i++) {
        if (data[i]['sort'] == '支出') {
            out_sum += parseFloat(data[i]['amount']);
            out_num++;
        } else {
            in_sum += parseFloat(data[i]['amount']);
            in_num++;
        }
    }
    if (count_year[year] == undefined) {
        count_year[year] = {};
        count_year[year]['out_sum'] = 0;
        count_year[year]['out_num'] = 0;
        count_year[year]['in_sum'] = 0;
        count_year[year]['in_num'] = 0;
    }
    count_year[year]['out_sum'] += out_sum;
    count_year[year]['out_num'] += out_num;
    count_year[year]['in_sum'] += in_sum;
    count_year[year]['in_num'] += in_num;
}

//交易序号
let order = 1;
let data_collection = {};


function ajax_one_month(offset) {
    function render_one_month(data, year, month) {
        //title
        let title = $('<div class="title"></div>');
        let title_month = $('<h2 class="month mr-4"></h2>').text(year + '年 ' + month + '月');
        //overall table
        let overall_table = $('<table class="table table-borderless" id="overall_table"></table>');
        let overall_tbody = $('<tbody></tbody>');
        let overall_tr_out = $('<tr class="text-success"></tr>')
            .append($('<td>支出</td>'))
            .append($('<td></td>').text(out_sum + '元'))
            .append($('<td></td>').text(out_num + '笔'));
        let overall_tr_in = $('<tr class="text-danger"></tr>')
            .append($('<td>收入</td>'))
            .append($('<td></td>').text(in_sum + '元'))
            .append($('<td></td>').text(in_num + '笔'));
        overall_tbody.append(overall_tr_out, overall_tr_in);
        overall_table.append(overall_tbody);
        title.append(title_month, overall_table);

        //table
        let table_div = $('<div class="table-responsive-md mt-4"></div>');
        let table = $('<table class="table"></table>');
        //thead
        let thead = $('<thead></thead>');
        thead.append($('<th>#</th>'));
        thead.append($('<th>序号</th>'))
        thead.append($('<th>类型</th>'));
        thead.append($('<th>金额</th>'));
        thead.append($('<th>项目</th>'));
        thead.append($('<th>时间</th>'));
        thead.append($('<th>经手人</th>'));
        thead.append($('<th>出(进)账人</th>'));
        thead.append($('<th>审核人</th>'));
        thead.append($('<th>备注</th>'));
        thead.append($('<th>操作</th>'));
        table.append(thead);
        //tbody
        let tbody = $('<tbody></tbody>')

        //tr
        function create_one_tr(data_e) {
            let tr = $('<tr></tr>')
            //tr class
            if (data_e['sort'] == '支出') {
                tr.addClass('outcome');
            } else {
                tr.addClass('income');
            }
            let checkbox = $('<td></td>').append($('<input type="checkbox">').val(data_e['amount']));
            let order_td = $('<td></td>').text(order);
            order++;
            let sort = $('<td></td>').text(data_e['sort']);
            let amount = $('<td></td>').text(data_e['amount']);
            let item = $('<td></td>').text(data_e['item']);
            let time = $('<td></td>').text(data_e['insert_time']);
            let first_hand = $('<td></td>').text(data_e['first_hand']);
            let cashier = $('<td></td>').text(data_e['cashier']);
            let auditor = $('<td></td>').text(data_e['auditor']);
            let remark = $('<td></td>').text(data_e['remark']);
            let operation = $('<td></td>');
            operation.append($('<a class="mr-3">更改</a>').attr('href', '/ledger/father/modify/change?id=' + data_e['id']));
            operation.append($('<a>删除</a>').attr('href', '/ledger/father/modify/delete?id=' + data_e['id']));
            tr.append(checkbox, order_td, sort, amount, item, time, first_hand, cashier, auditor, remark, operation);
            return tr;
        }

        for (let i = 0; i < data.length; i++) {
            tbody.append(create_one_tr(data[i]));
        }
        table.append(tbody);

        table_div.append(table);

        //card
        let card = $('<div class="card mt-4"></div>');
        let card_body = $('<div class="card-body"></div>').append(title, table_div);
        card.append(card_body);
        return card;
    }

    $.ajax({
        url: '/ledger/father/ajax/load',
        type: 'GET',
        async: false,
        data: 'offset=' + offset,
        dataType: 'json',
        success: function (data) {
            let month = new Date().getMonth() + 1;
            let year = new Date().getFullYear();
            //年月计算
            let year_offset = 0;
            while (offset > month) {
                month += 12;
                year_offset++;
            }
            month = month - offset;
            year = year - year_offset;
            //将data存入data_collection
            const property_name = String(year) + '-' + String(month);
            data_collection[property_name] = data;

            title_month_overall_calc(data, year);
            let card = render_one_month(data, year, month);
            $('#main_container').append(card);
            out_num = out_sum = in_sum = in_num = 0;
        }
    })
}

const data_collection_sample = {
    '2020-7': [
        {
            "amount": "123",
            "auditor": "\u4f0d\u5cb3\u658c",
            "cashier": "\u4f0d\u5cb3\u658c",
            "first_hand": "\u4f0d\u5cb3\u658c",
            "id": 1,
            "item": "123",
            "remark": "123",
            "sort": "\u652f\u51fa",
            "insert_time": "2020-07-30"
        },
        {
            "amount": "123",
            "auditor": "\u4f0d\u5cb3\u658c",
            "cashier": "\u4f0d\u5cb3\u658c",
            "first_hand": "\u4f0d\u5cb3\u658c",
            "id": 1,
            "item": "123",
            "remark": "123",
            "sort": "\u652f\u51fa",
            "insert_time": "2020-07-30"
        }
    ]
}
let count_staff_result_sample = {
    'first_hand': {'xx': 123},
    'cashier_in': {'xx': 234},
    'cashier_out': {},
    'auditor': {}
}


$(document).ready(function () {
    //ajax
    const all_offset_str = $('#all_offset').text().slice(1, -1).split(',');
    if (all_offset_str[0] == '') {
        $('#main_container').append($('<p class="text-muted text-center" style="font-size: 3rem">当前无记录</p>'))
    } else {
        for (let i = 0; i < all_offset_str.length; i++) {
            let offset = parseInt(all_offset_str[i]);
            ajax_one_month(offset);
        }
    }
    //统计勾选项
    $('#count_checked').click(function () {
        let sum = 0;
        let num = 0;
        $(':checkbox').filter(':checked').each(function () {
            sum += parseInt($(this).val());
            num++;
        })
        $('#count_checked_modal .modal-body').text('总计' + num + '笔 共' + sum + '元');
        $('#count_checked_modal').modal('show');
    })
    //统计人员项
    $('#count_staff').click(function () {
        $('#count_staff_modal').modal('show');
    })
    $('#query').click(function () {
        //删除之前的查询
        $('#count_staff_modal .table-borderless').remove();
        $('#count_staff_modal hr').remove();
        $('#count_staff_modal .text-muted').remove();

        const query_year = $('#year').val();
        const query_month = $('#month').val();
        const query_sort_convert = {'经手人': 'first_hand', '出账人': 'cashier_out', '进账人': 'cashier_in', '审核人': 'auditor'};
        const query_sort = query_sort_convert[$('#query_sort').val()];
        //initial count_staff_result
        const staff = ['伍岳斌', '杨晟', '胡冬冬', '吕志武', '吴帅', '宋基元', '海南津杭', '湖北恒创', '湖北佳境'];
        const staff_type = ['first_hand', 'cashier_in', 'cashier_out', 'auditor'];
        let count_staff_result = {};
        for (let i = 0; i < staff_type.length; i++) {
            count_staff_result[staff_type[i]] = {};
            for (let k = 0; k < staff.length; k++) {
                count_staff_result[staff_type[i]][staff[k]] = 0;
            }
        }
        //查询
        const property_name = query_year + '-' + query_month;
        if (!data_collection[property_name]) {
            $('#count_staff_modal .modal-body').append($('<hr>'), $('<p class="text-muted text-center">该月无记录</p>'));
        } else {
            for (let i = 0; i < data_collection[property_name].length; i++) {
                let e = data_collection[property_name][i];
                e['amount'] = parseInt(e['amount']);
                if (e['sort'] == '支出') {
                    count_staff_result['first_hand'][e['first_hand']] += e['amount'];
                    count_staff_result['cashier_out'][e['cashier']] += e['amount'];
                    count_staff_result['auditor'][e['auditor']] += e['amount'];
                } else {
                    count_staff_result['first_hand'][e['first_hand']] += e['amount'];
                    count_staff_result['cashier_in'][e['cashier']] += e['amount'];
                    count_staff_result['auditor'][e['auditor']] += e['amount'];
                }
            }
            let result_table = $('<table class="table table-borderless"></table>');
            let result_table_thead = $('<thead><tr><th>人员</th><th>金额</th></tr></thead>')
            let result_table_body = $('<tbody></tbody>');
            for (let property in count_staff_result[query_sort]) {
                let obj = count_staff_result[query_sort];
                let tr = $('<tr></tr>');
                tr.append($('<td></td>').text(property));
                tr.append($('<td></td>').text(obj[property]));
                result_table_body.append(tr);
            }
            result_table.append(result_table_thead, result_table_body);

            let hr = $('<hr>')
            $('#count_staff_modal .modal-body').append(hr, result_table);
        }
    })
    //按年统计
    $('#count_year').click(function () {
        let table = $('<table class="table"></table>');
        let thead = $('<thead><tr><th>年份</th><th>支出</th><th>支出笔数</th><th>收入</th><th>收入笔数</th></tr></thead>');
        let tbody = $('<tbody></tbody>');
        for (let year in count_year) {
            $('#count_year_modal .modal-body');
            let tr = $('<tr></tr>');
            tr.append('<td>' + year + '</td>');
            tr.append('<td>' + count_year[year]['out_sum'] + '</td>');
            tr.append('<td>' + count_year[year]['out_num'] + '</td>');
            tr.append('<td>' + count_year[year]['in_sum'] + '</td>');
            tr.append('<td>' + count_year[year]['in_num'] + '</td>');
            tbody.append(tr);
        }
        table.append(thead, tbody);
        $('#count_year_modal .modal-body').append(table);
        $('#count_year_modal').modal('show');
    })
})