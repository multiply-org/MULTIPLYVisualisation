import numpy as np
import gdal
import xarray as xr
import plotly
import plotly.plotly as py
import plotly.offline as py_off
from plotly.graph_objs import *
import glob
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies
import datetime as dt
from dash.dependencies import Input, Output


# find the parameter names available
pnames = list(np.unique([j.split('_')[0].split('/')[1] for j in sorted(glob.glob('data/*.tif'))]))

# give it a style sheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

access_token = 'pk.eyJ1IjoiYWxleGNvcm5lbGl1cyIsImEiOiJjandhcXZ2ZnMwYnB0NDlzNnJyYXF2NGh5In0.dOemdsmJJfkte6eeoBrQbQ'

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# this sets up the empty app

data = []
  
input_value = 'lai'
  
pfiles = sorted(glob.glob('data/%s*.tif'%input_value))

if len(pfiles) == 0:
    pfiles = sorted(glob.glob('data/lai*.tif'))

pfiles = [i for i in pfiles if 'unc' not in i]

time = []

for n,fname in enumerate(pfiles):

    print (fname)

    tmp_name = 'tmp_%s.vrt'%n

    # convert to lat/lon
    gdal.Warp(
        srcDSOrSrcDSTab=fname,
        destNameOrDestDS=tmp_name,
        format='VRT',
        dstSRS = 'EPSG:4326')

    # open the data set
    ds = xr.open_rasterio(tmp_name)

    # take  subset around some interesting bits for speed
    ds = ds.isel(x=range(50,100),y=range(125,175))

    # convert it to a 2 dimensional dataframe
    df = ds.to_dataframe('lai')

    # pull out the usefull bits from the nested index
    # this is so the data knows where to put itself
    df['latitude'] = df.index.get_level_values('y')
    df['longitude'] = df.index.get_level_values('x')

    date_bits = fname.split('_')[1][1:8]
    year = int(date_bits[:4])
    doy = int(date_bits[4:])
    stamp = (dt.datetime(year,1,1) + dt.timedelta(hours = 24*doy))
    time.append(stamp)

    # add each scenes data to the repository
    data.append(
    Scattermapbox(
        lon=df['longitude'].values,   # lon goes here
        lat=df['latitude'].values,    # lat goes here
        mode='markers',
        marker=scattermapbox.Marker(
            size=18,
            color=df['lai'].values,
            showscale=True)))

    os.remove(tmp_name)

mapbox=dict(
    accesstoken=access_token,
    bearing=0,
    center=dict(
        lat=np.mean(df['latitude'].values),   # where to center the map in initsiatlization
        lon=np.mean(df['longitude'].values)
    ),
    pitch=0,zoom=15,
    style='light'
)
    
app.layout = html.Div( children=[
    
    html.H1(children='A demonstation on pulling out a pixels timeries',
            style = {'color': [0,141./256,165./256], 'textAlign': 'center'}),

    html.Div(id='out_pixel'),

    html.Div(dcc.Graph(id='scatter_of_data',
                                 figure={'data': [data[1]],'layout': {'mapbox': mapbox}}))])

@app.callback(
    dash.dependencies.Output(component_id = 'out_pixel', component_property = 'children'),
    [dash.dependencies.Input(component_id = 'scatter_of_data', component_property = 'hoverData')])
def update(thing_to_print):
    try:
        lat = thing_to_print['points'][0]['lat']
        lon = thing_to_print['points'][0]['lon']
        lat_ind = np.where(ds['y'].values == lat)[0][0]
        lon_ind = np.where(ds['x'].values == lon)[0][0]
        return 'New index in the data %s %s'%(str(lat_ind),str(lon_ind))

    except:
        pass

if __name__ == '__main__':
    app.run_server(debug=True)
