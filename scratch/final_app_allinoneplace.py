#######################################################
#
# The dash app
#
# Created on:      17-Jun-2019
# Original author: Bethan Perkins
#
#######################################################

import os
import numpy as np
import datetime as dt
import pandas as pd

import dash

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objs as go

from src.DataHandling import DataHandling



def generate_dropdown():
    """
    Build the 'select parameter' dropdown
    :return:
    """
    dropdown  = html.Div(dcc.Dropdown(id='parameter_select',
                          options=[{'label': i, 'value': i} for i in all_parameters],),
             style={'width':'100px', 'display': 'inline-block'})

    return dropdown

def build_slider(timesteps):
    """
    Create the slider which displays the timesteps of the data
    :return:
    """
    slider = dcc.Slider(
        id='time-slider',
        min=dt.datetime.timestamp(timesteps[0]),
        max=dt.datetime.timestamp(timesteps[-1]),
        value=dt.datetime.timestamp(timesteps[0]),
        marks={dt.datetime.timestamp(timestep): timestep.strftime("%Y-%m-%d") for timestep in timesteps},
        step=None,
    )

    return slider


def create_map(df, unc=False):
    """
    Build the map
    """

    if not unc:
        data = df['mean'].values
        v_elements = {
            'cmin': float(df['mean'].mean() - 2*df['mean'].std()),
            'cmax': float(df['mean'].mean() + 2*df['mean'].std()),
            'colorscale': 'RdBu',
        }
    else:
        data = df['max'].values - df['min'].values
        #todo: clean this up
        v_elements = {
        'cmin': 0,
        'cmax': float(df['mean'].min() + 2*df['mean'].std()),
        'colorscale': 'Viridis',
        }


    data = go.Scattermapbox(
        lon=df.index.get_level_values('longitude').values,
        lat=df.index.get_level_values('latitude').values,
        hovertext=df['mean'].values.astype(str),
        hoverinfo='text',
        mode='markers',
        marker={
            'size': 10,
            'color': data,
            'symbol': 'circle',
            'cmin': v_elements['cmin'],
            'cmax': v_elements['cmax'],
            'colorscale': v_elements['colorscale'],
            'showscale': True,
        }
    )

    layout = go.Layout(
        margin=dict(t=0, b=0, r=10, l=10),
        autosize=True,
        hovermode='closest',
        showlegend=False,
        mapbox=dict(
            accesstoken='pk.eyJ1IjoiYmV0aGFucGVya2lucyIsImEiOiJpZ1lWQXlzIn0.comSgcNvpNUaLuXE0EOc8A',
            bearing=0,
            center=dict(
                lat=np.mean(df.index.get_level_values('latitude').values),
                lon=np.mean(df.index.get_level_values('longitude').values)
            ),
            pitch=0,
            zoom=13,
            style='light'
        )
    )

    return {'data': [data], 'layout': layout}

def create_timeseries_plot(df, param):
    """

    :param df:
    :return:
    """

    time = [pd.to_datetime(t).strftime("%d-%m-%Y") for t in df.index.values]

    mean_line = go.Scatter(
        x=time,
        y=df['mean'],
        mode='lines+markers',
        name='mean',
        marker={'color': 'rgba(0,150,150)'},
        error_y=dict(
            type='data',
            symmetric=False,
            array=df['max']-df['mean'],
            arrayminus=df['mean']-df['min']
        )
    )

    maxmin_fill = go.Scatter(
        x=time + time[::-1], # time forwards and then backwards
        y=pd.concat([df['max'], df['min'][::-1]]),
        fill='tozerox',
        fillcolor='rgba(0,150,150, 0.5)',
        line=dict(color='rgba(0,150,150, 0)'),
        name='Range')



    data = [mean_line, maxmin_fill]

    layout = go.Layout(
            xaxis={'title': "Timestep"},
            yaxis={'title': param})

    return {'data': data, 'layout': layout}



app = dash.Dash(__name__)

server = app.server

app.config['suppress_callback_exceptions']=True

#data_directory = os.path.abspath('../data/')

dh = DataHandling(data_directory)

all_parameters = dh.get_available_parameters()


# Setup page
app.layout = html.Div([
    html.H1(children='Multiply Visulisation', style={'textAlign': 'center'}),
    html.Div([dcc.Markdown(id='markdown', children="default text")]),
    generate_dropdown(),
    html.Button(id='select',  n_clicks=0, children='Select'
    ),
    html.Div(
        id='slider-container',
        style={'width': '80%', 'display':'inline-block', 'margin-bottom':'40px', 'height':'40px'},
        children=""
    ),
    html.Div(
        style={'width': '40%', 'float':'left', 'display':'inline-block'},
        children=[dcc.Graph(id='core-map')]
        ),
    html.Div(
        style={'width': '40%', 'float':'left', 'display':'inline-block'},
        children=[dcc.Graph(id='unc-map'),]
        ),
    html.Div(
        style={'width': '80%', 'float':'left', 'display':'inline-block'},
        children=dcc.Graph(id='pixel_timeseries'))
])

@app.callback(Output(component_id='pixel_timeseries', component_property='figure'),
              [Input(component_id='core-map', component_property='clickData'),
              Input(component_id='unc-map', component_property='clickData')],
              [State(component_id='parameter_select', component_property='value')])
def update_timeseries(location_info1, location_info2, parameter):
    """

    :param location_info:
    :return:
    """

    # Isolate the input which has triggered this callback
    trigger = dash.callback_context.triggered[0]

    if trigger['value']:

        # Update latitude and longitude from map click
        latitude = trigger['value']['points'][0]['lat']
        longitude = trigger['value']['points'][0]['lon']

        # Extract the timeseries from the dataframe
        dataframe = dh.get_timeseries(parameter, latitude, longitude)

        # Create ht timeseries plot
        timeseries_plot = create_timeseries_plot(dataframe, parameter)

        return timeseries_plot

    else:

        return {}


@app.callback(Output(component_id='slider-container', component_property='children'),
              [Input('select', 'n_clicks')],
              [State(component_id='parameter_select', component_property='value')])
def initialise_slider(n_clicks, parameter):

    if n_clicks:

        # Build the slider
        timesteps = dh.get_timesteps(parameter)
        slider = build_slider(timesteps)

        return slider

    else:
        pass

# Update the 'data' map to reflect the position of the time slider
@app.callback([Output(component_id='core-map', component_property='figure'),
               Output(component_id='unc-map', component_property='figure')],
              [Input('time-slider', 'value')],
              [State(component_id='parameter_select', component_property='value')])
def update_maps(timestamp, parameter):

    # Convert timestamp to datetime
    dtime = dt.datetime.fromtimestamp(timestamp)

    # Extract this data
    df = dh.get_timestep(parameter, time=dtime)

    # Build the maps
    core_map = create_map(df)
    unc_map = create_map(df, unc=True)

    return core_map, unc_map


@app.callback(
    Output('markdown', 'children'),
    [Input('time-slider', 'value')])
def update_markup(selected_time):
    """
    Post the date of the marker to the markdown string to make sure we're seeing time updating
    :param selected_time:
    :return:
    """
    return dt.datetime.fromtimestamp(selected_time).strftime("%Y-%m-%d")