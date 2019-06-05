import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.plotly as py
import plotly.graph_objs as go

import glob
import gdal
import xarray as xr
import os
import numpy as np
import pandas as pd

import re
import datetime as dt

import time

app = dash.Dash(__name__)
access_token='pk.eyJ1IjoiYmV0aGFucGVya2lucyIsImEiOiJpZ1lWQXlzIn0.comSgcNvpNUaLuXE0EOc8A'

def build_df(ext, unc=False):
    """
    Create the dataframe of the compressed xarray of all the data
    """

    # Extract files
    if unc:
        files = sorted(glob.glob('../data/{}_A???????_unc.tif'.format(ext)))
    else:
        files = sorted(glob.glob('../data/{}_A???????.tif'.format(ext)))

    # Set flag to be false so that a new xarray is created the first time around
    first_timestep_complete = False

    for n, fname in enumerate(files):

        tmp_file = 'tmp_{}.vrt'.format(n)

        # convert to lat/lon
        gd = gdal.Warp(
            srcDSOrSrcDSTab=fname,
            destNameOrDestDS=tmp_file,
            format='VRT',
            dstSRS = 'EPSG:4326')
        gd = None # flush the file 

        # open the data set
        ds = xr.open_rasterio(tmp_file)

        # rename dimensions
        ds = ds.rename({'band': 'time', 'x': 'longitude', 'y':'latitude'})

        # Extract the date from the filename and create time coordinate
        datestring = (re.findall('\d+', fname))[0]
        date = dt.datetime.strptime(datestring, "%Y%j")
        ds.time.values = [date]

        if not first_timestep_complete:

            output = ds
            first_timestep_complete = True

        # For runs >1, concatenate to the existing output variable
        else:

            output = xr.concat([output, ds], dim='time')

        # Delete the temporary file
        os.remove(tmp_file)

    # convert the large xarray into a large dataframe
    df = output.to_dataframe('data')        

    return df

def define_vis_elements(df, unc=False):
        # Define differnces for full data vs related uncertainty
    if not unc:
        v_elements = {
            'cmin': float(df['data'].mean() - 2*df['data'].std()),
            'cmax': float(df['data'].mean() + 2*df['data'].std()),
            'colorscale': 'RdBu',
        }
    else:
        v_elements = {
        'cmin': 0,
        'cmax': float(df['data'].min() + 2*df['data'].std()),
        'colorscale': 'Viridis',
        }

    return v_elements


def create_map(df, vis_elements, unc=False):
    """
    Build the map
    """

    data = go.Scattermapbox(
        lon=df.index.get_level_values('longitude').values,
        lat=df.index.get_level_values('latitude').values,
        hovertext=df['data'].values.astype(str),
        hoverinfo='text',
        mode='markers',
        marker={
            'size':10,
            'color':df['data'].values,
            'symbol':'circle',
            'cmin': vis_elements['cmin'],
            'cmax':  vis_elements['cmax'],
            'colorscale':  vis_elements['colorscale'],
            'showscale': True,
            }
        )
    
    layout = go.Layout(
                margin=dict(t=0,b=0,r=10,l=10),
                autosize=True,
                hovermode='closest',
                showlegend=False,
                mapbox=dict(
                    accesstoken=access_token,
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


# Generate both data and uncertainty xarrays
data_df = build_df('lai')
unc_df = build_df('lai', unc=True)

# Create key values for the visulaistaion (e.g. max/min etc)
data_vis = define_vis_elements(data_df)
unc_vis = define_vis_elements(unc_df, unc=True)

# Extract timesteps from the data array
# Todo: check here to make sure that the unc array timesteps are the same, take the intersection
timesteps = data_df.index.get_level_values('time').values

# Build the date slider
slider = dcc.Slider(
    id='time-slider',
    min=timesteps.min().astype('int64'),
    max=timesteps.max().astype('int64'),
    value=timesteps[0].astype('int64'),
    marks={timestep.astype('int64'):str(timestep)[:10]  for timestep in timesteps},
    step=None,
)

# Setup page
app.layout = html.Div([
    html.H1("Test 14: Maps with a slider"),
    html.Div([dcc.Markdown(id='markdown', children="default text")]),
    html.Div(style={'width': '80%', 'display':'inline-block', 'margin-bottom':'40px'}, children=[slider]),
    html.Div(
        style={'width': '40%', 'float':'left', 'display':'inline-block'}, 
        children=[dcc.Graph(id='the-map')]
        ),
    html.Div(
        style={'width': '40%', 'float':'left', 'display':'inline-block'}, 
        children=[dcc.Graph(id='the-unc-map'),]
        ),
])


# Update the markdown with the title
@app.callback(
    Output('markdown', 'children'),
    [Input('time-slider', 'value')])   
def update_markup(selected_time):
    return "{}".format(pd.to_datetime(selected_time))

#Update the 'data' map
@app.callback(
    Output('the-map', 'figure'),
    [Input('time-slider', 'value')]) 
def update_data_figure(selected_time):
    selected_time_dt = pd.to_datetime(selected_time)
    filtered_df = data_df[data_df.index.get_level_values('time') == selected_time_dt]
    return create_map(filtered_df, data_vis)
    
#Update the 'uncertainty' map
@app.callback(
    Output('the-unc-map', 'figure'),
    [Input('time-slider', 'value')]) 
def update_unc_figure(selected_time):
    selected_time_dt = pd.to_datetime(selected_time)
    filtered_df = unc_df[unc_df.index.get_level_values('time') == selected_time_dt]
    return create_map(filtered_df, unc_vis, unc=True)


if __name__ == '__main__':
    app.run_server(debug=True)