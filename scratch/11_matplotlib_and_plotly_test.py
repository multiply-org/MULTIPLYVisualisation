import dash
import dash_core_components as dcc
import dash_html_components as html

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
import plotly.plotly as py
from plotly.tools import mpl_to_plotly

app = dash.Dash()

## Generating the data..
x =  np.linspace(np.pi, 3*np.pi, 1000)
sinx = np.sin(x)
logx = np.log(x)

# Creating the matplotlib graph..
mpl_fig = plt.figure()
ax = mpl_fig.add_subplot(111)
ax.plot(x, sinx)
ax.set_title('A Sine Curve')

# Converting to Plotly's Figure object..
plotly_fig = mpl_to_plotly(mpl_fig)

graph = dcc.Graph(id='myGraph', figure=plotly_fig)

app.layout = html.Div([graph])


if __name__ == '__main__':
    app.run_server(debug=True)