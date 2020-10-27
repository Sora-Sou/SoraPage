from flask import Blueprint, render_template, request, redirect, jsonify, flash

exp = Blueprint('exp', __name__, template_folder='./', static_folder='./')


@exp.route('/experiment/idsel', methods=['POST', 'GET'])
def idsel():
    if request.method == 'GET':
        return render_template('impurity_distribution_of_Si_epitaxial_layer.html')
    elif request.method == 'POST':
        data = request.get_json()
        # {'Q_S1': ['123', '123'], 'Q_S2': [], 'CV_S1': ['123', '123'], 'CV_S2': []}
        for value in data.values():
            for i in range(len(value)):
                value[i] = float(value[i])
        from experiment.impurity_distribution_of_Si_epitaxial_layer import data_process
        data_process(data)
        return "success"
