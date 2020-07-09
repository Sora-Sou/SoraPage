from flask import Blueprint, render_template

ACGN = Blueprint('ACGN', __name__, template_folder='ACGN_html', static_folder='ACGN_static')


@ACGN.route('/ACGN')
def acgn():
    myDict = {
        'name': '金色loveriche',
        'type': 'Galgame',
        'rank': 'S',
        'img_length': 2,
        'character': {'公主': 'S-', '玲奈': 'A+'},
        'script': 'A-',
        'music': 'S-',
        'character_rank': 'A+',
        'cg': 'S-',
        'finish_date': '2020.6.30'
    }
    rank_visualize = {
        'S': [5, 100],
        'S-': [4.5, 90],
        'A+': [4, 80],
        'A': [3.5, 70],
        'A-': [3, 60],
        'B': [2.5, 50]
    }
    return render_template('ACGN.html', cardDict_py=myDict, rank_visualize=rank_visualize)
