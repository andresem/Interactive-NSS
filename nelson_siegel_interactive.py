from bokeh.plotting import figure
from bokeh.layouts import layout
from bokeh.models import Button, ColumnDataSource, Slider, TextInput
from bokeh.io import curdoc
import numpy as np
from scipy.optimize import minimize
from sklearn.metrics import mean_squared_error

def nelson_siegel_svensson(points, b0, b1, b2, b3, tau, tau2):
    """
    Function that calculate the rates for a serie of points using the 
    Nelson-Siegel-Svensson's model.
    
    Parameters
    ----------
    points : list
        A list that include the times in years to calculate the rates. 
    b0, b1, b2, b3, tau, tau2: float
        Parameters that fit the points with the curve.
    Returns
    -------
    ndarray
        Array with the rates for the times t in the array called points.

    """
    points = np.array(points)
    part1 = b0 + b1*(1-np.exp(-points/tau))/(points/tau)
    part2 = b2*((1-np.exp(-points/tau)/(points/tau))-np.exp(-points/tau))
    part3 = b3*((1-np.exp(-points/tau2)/(points/tau2))-np.exp(-points/tau2))
    return  part1 + part2 + part3

def optimization_nss(params, points, y):
    """
    Function to optimize the parameters of the Nelson-Siegel-Svensson model.
    
    Parameters
    ----------
    params : list
        Parameters to optimize (b0, b1, b2, b3, tau, tau2)
    points : list
        A list with the initial times in years to fit the curve.
    y : list
        A list with the rates that correspond to each time in the list of points.

    Returns
    -------
    float
        Root mean square error of the real rates with the calculated using 
        the Nelson-Siegel-Svensson model.

    """
    points = np.array(points)
    y_pred = nelson_siegel_svensson(points, params[0], params[1], 
                                    params[2], params[3], params[4], 
                                    params[5])
    return mean_squared_error(y, y_pred)


years_edit  = TextInput(title = 'Years', value = '[1, 2, 3]')
rates_edit = TextInput(title = 'Rates', value = '[0.5, 0.6, 0.8]')
button = Button(label = 'Fit curve', button_type = 'success')

source = ColumnDataSource(data = dict(x = eval(years_edit.value), 
                                      y = eval(rates_edit.value)))

TOOLTIPS = [
    ("Time", "$x"),
    ("Rate", "$y")
]

p = figure(x_range = (0, 30), plot_width = 1000, plot_height = 350, tooltips = TOOLTIPS)

p.xaxis.axis_label = "Time (Years)"

p.yaxis.axis_label = "Rate (%)"
p.yaxis.major_label_orientation = "vertical"


resutls_nss = minimize(optimization_nss, np.array([0, 0, 0, 0, 1, 1]), 
                       (eval(years_edit.value), 
                        eval(rates_edit.value)), 
                       bounds = ((0, np.inf), (-np.inf, np.inf), (-np.inf, np.inf), (-np.inf, np.inf), (0, np.inf), (0, np.inf)))

resutls_nss_b = minimize(optimization_nss, np.array([0, 0, 0, 0, 1, 1]), 
                         (eval(years_edit.value), 
                          eval(rates_edit.value)))

slider_b0 = Slider(start = 0, end = resutls_nss.x[0] + 10, value = resutls_nss.x[0], step = 0.01, title = "β₀")
slider_b1 = Slider(start = resutls_nss.x[1] - 2, end = resutls_nss.x[1] + 2, value = resutls_nss.x[1], step = 0.01, title = "β₁")
slider_b2 = Slider(start= -2, end = 2, value = resutls_nss.x[2], step = 0.01, title = "β₂")
slider_b3 = Slider(start = -2, end = 2, value = resutls_nss.x[3], step = 0.01, title = "β₃")
slider_tau1 = Slider(start = 0, end = 10, value = resutls_nss.x[4], step = 0.01, title = "τ₁")
slider_tau2 = Slider(start = 0, end = 2, value = resutls_nss.x[5], step = 0.01, title = "τ₂")

x = np.linspace(1, 30, 300)
line_ns = p.line(x = x, y = nelson_siegel_svensson(x, *resutls_nss.x), line_width = 2, legend_label = 'Nelson-Siegel-Svensson')
circles = p.circle(source = source, size = 8, color = 'orange', legend_label = 'Real')
  

def change_value(attr, old, new):
    y = nelson_siegel_svensson(x, slider_b0.value, slider_b1.value, slider_b2.value, 
                               slider_b3.value, slider_tau1.value, slider_tau2.value)
    source = ColumnDataSource(data = dict(x = x, y = y))
    line_ns.data_source.data['y'] = source.data['y']
    
def fit_curve():
    resutls_nss = minimize(optimization_nss, np.array([0, 0, 0, 0, 1, 1]), 
                       (eval(years_edit.value), 
                        eval(rates_edit.value)), 
                       bounds = ((0, np.inf), (-np.inf, np.inf), (-np.inf, np.inf), (-np.inf, np.inf), (0, np.inf), (0.0001, np.inf)))
    y = nelson_siegel_svensson(x, *resutls_nss.x)    
    source = ColumnDataSource(data = dict(x = x, y = y))
    line_ns.data_source.data['y'] = source.data['y']
    
    source = ColumnDataSource(data = dict(x = eval(years_edit.value), y = eval(rates_edit.value)))
    circles.data_source.data['x'] = source.data['x']
    circles.data_source.data['y'] = source.data['y']
    slider_b0.update(value = resutls_nss.x[0], 
                     start = 0, 
                     end = resutls_nss.x[0] + 10)
    slider_b1.update(value = resutls_nss.x[1], 
                     start = resutls_nss.x[1] - 10, 
                     end = resutls_nss.x[1] + 10)
    slider_b2.update(value = resutls_nss.x[2], 
                     start = resutls_nss.x[2] - 2, 
                     end = resutls_nss.x[2] + 2)
    slider_b3.update(value = resutls_nss.x[3], 
                     start = resutls_nss.x[3] - 2, 
                     end = resutls_nss.x[3] + 2)
    slider_tau1.update(value = resutls_nss.x[4], 
                     start = 0, 
                     end = resutls_nss.x[4] + 2)
    slider_tau2.update(value = resutls_nss.x[5], 
                     start = 0, 
                     end = resutls_nss.x[5] + 2)
    
p.legend.click_policy = "hide"

layout = layout([[years_edit, rates_edit],
                 [slider_b0, slider_b1, ],
                 [slider_b2, slider_b3],
                 [slider_tau1, slider_tau2],
                 [button], [p]])

button.on_click(fit_curve)
slider_b0.on_change('value', change_value)
slider_b1.on_change('value', change_value)
slider_b2.on_change('value', change_value)
slider_b3.on_change('value', change_value)
slider_tau1.on_change('value', change_value)
slider_tau2.on_change('value', change_value)

curdoc().add_root(layout)