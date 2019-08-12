import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly
import plotly.graph_objs as go


app = dash.Dash()

trace1 = go.Scatter(
    x=[1, 2, 3],
    y=[2, 3, 4],
    name="trace 1",
)
trace2 = go.Scatter(
    x=[20, 30, 40],
    y=[5, 5, 5],
    name="trace 2",
    xaxis='x7',
    yaxis='y'
 )
trace3 = go.Scatter(
    x=[2, 3, 4],
    y=[600, 700, 800],
    name="trace 3",
    xaxis='x',
    yaxis='y2'
)
trace4 = go.Scatter(
    x=[4000, 5000, 6000],
    y=[7000, 8000, 9000],
    name="trace 4",
    xaxis='x7',
    yaxis='y2'
)
data = [trace1, trace2, trace3, trace4]

layout = go.Layout(
    xaxis=dict(
        domain=[0, 0.45]
    ),
    yaxis=dict(
        domain=[0, 0.45]
    ),
    xaxis7=dict(
        domain=[0.55, 1]
    ),
    yaxis2=dict(
        domain=[0.55, 1],
    ),
)
plotly_figure = go.Figure(data=data, layout=layout)

text = '''
Test of plotting surface raster plot in a dash.
'''

graph = dcc.Graph(id='myGraph', figure=plotly_figure)

app.layout = html.Div([
	dcc.Markdown(children=text),
	graph,
	])

if __name__ == '__main__':
    app.run_server(debug=True)