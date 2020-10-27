import numpy as np
import math
import matplotlib.pyplot as plt


def data_process(data):
    Q_S1 = {
        'V': np.array([10, 20, 30, 40, 50, 60, 70, 80, 85]),
        'C': np.array(data['Q_S1'])
    }

    Q_S1['CT'] = 4 * (250.2 - Q_S1['C']) / math.pi
    Q_S1['x'] = np.log10(Q_S1['V'] + 0.5)
    Q_S1['y'] = np.log10(Q_S1['CT'])

    fit_res = np.polyfit(Q_S1['x'], Q_S1['y'], 1)
    k = fit_res[0]
    b = fit_res[1]
    print(fit_res)

    equation = np.poly1d([k, b])
    Q_S1['fit_y'] = equation(Q_S1['x'])

    plt.plot(Q_S1['x'], Q_S1['fit_y'])
    plt.scatter(Q_S1['x'], Q_S1['y'])
    plt.show()