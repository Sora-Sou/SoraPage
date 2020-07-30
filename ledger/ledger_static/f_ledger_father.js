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
        "time": "2020-07-30"
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
        "time": "2020-07-30"
    }
]


let out_sum = 0;
let out_num = 0;
let in_sum = 0;
let in_num = 0;

function title_month_overall_calc(data) {
    for (let i = 0; i < data.length; i++) {
        if (data[i]['sort'] == '支出') {
            out_sum += parseFloat(data[i]['amount']);
            out_num++;
        } else {
            in_sum += parseFloat(data[i]['amount']);
            in_num++;
        }
    }
}

offset = 0;
const month = new Date().getMonth() + 1;
//交易序号
let order = 0;

function ajax_one_month() {
    function render_one_month(data) {
        //title
        let title = $('<div class="title"></div>');
        let title_month = $('<h2 class="month mr-4"></h2>').text((month - offset) + '月');
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
        thead.append($('<th>类型</th>'));
        thead.append($('<th>金额</th>'));
        thead.append($('<th>项目</th>'));
        thead.append($('<th>时间</th>'));
        thead.append($('<th>经手人</th>'));
        thead.append($('<th>出(进)账人</th>'));
        thead.append($('<th>审核人</th>'));
        thead.append($('<th>备注</th>'))
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
            let order_td = $('<td></td>').text(order);
            order++;
            let sort = $('<td></td>').text(data_e['sort']);
            let amount = $('<td></td>').text(data_e['amount']);
            let item = $('<td></td>').text(data_e['item']);
            let time = $('<td></td>').text(data_e['time']);
            let first_hand = $('<td></td>').text(data_e['first_hand']);
            let cashier = $('<td></td>').text(data_e['cashier']);
            let auditor = $('<td></td>').text(data_e['auditor']);
            let remark = $('<td></td>').text(data_e['remark']);
            tr.append(order_td, sort, amount, item, time, first_hand, cashier, auditor, remark);
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
            title_month_overall_calc(data);
            let card = render_one_month(data);
            $('#main_container').append(card);
            offset++;
            out_num = out_sum = in_sum = in_num = 0;
        }
    })
}

$(document).ready(function () {
    ajax_one_month();
})