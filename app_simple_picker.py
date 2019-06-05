import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np
import glob

pnames = list(np.unique([j.split('_')[0].split('/')[1] for j in sorted(glob.glob('data/*.tif'))]))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# this sets up the empty app

app.layout = html.Div( children=[
    
    html.H1(children='Pick an option:', style = {'color': '#7FDBFF', 'textAlign': 'center'}),
    
    html.Div(dcc.RadioItems(id='radio_input',options=[{'label': i, 'value': i} for i in pnames],
                             labelStyle={'display': 'inline-block', 'textAlign': 'center'}),
              style={'float': 'right', 'display': 'inline-block'}),
    
    # notice no children as we will specify these later with the callback
    html.Div(id='output')
    
    
    
])
    
# now we setup the call back

@app.callback(
    # first put in what we want to happen with output, by saying which component we want,
    # and what we actually want to change about it - the child (the text value it has)
    Output(component_id = 'output', component_property = 'children'),
    
    # Next we specifiy what we want to take out of the what ha shappened from the app
    # this is the output from the radiobuttons and wqe wand the value from it
    [Input(component_id = 'radio_input', component_property = 'value')]
)    
    # when this call back occurs, the radion input is automatically returned and used 
    # as the argument for whatever function we give below. Whatever is returned from th
    # is the function is then given to Output, which changes the 'output' component by 
    # altering the child.
    
def update_the_param(input_value):
    
    return 'Available files are:\n%s'%(sorted(glob.glob('data/%s*'%input_value)))
     

if __name__ == '__main__':
    app.run_server(debug=True)
    