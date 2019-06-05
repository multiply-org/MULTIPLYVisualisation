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
import plotly.graph_objs as go
from dash.dependencies import Input, Output

# >>>>>>>>>> SETUP
# find the parameter names available
pnames = list(np.unique([j.split('_')[0].split('/')[1] for j in sorted(glob.glob('data/*.tif'))]))

# give it a style sheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

access_token = 'pk.eyJ1IjoiYWxleGNvcm5lbGl1cyIsImEiOiJjandhcXZ2ZnMwYnB0NDlzNnJyYXF2NGh5In0.dOemdsmJJfkte6eeoBrQbQ'

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# this sets up the empty app

# >>>>>>>>>>> COMPILE 3D ARRAY OF DATA
data = []
  
input_value = 'lai'
  
pfiles = sorted(glob.glob('../data/%s*.tif'%input_value))

if len(pfiles) == 0:
    pfiles = sorted(glob.glob('../data/lai*.tif'))

pfiles = [i for i in pfiles if 'unc' not in i]

time = []

for n,fname in enumerate(pfiles):

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

    if n == 0:
        dcube = np.zeros([len(pfiles), ds[0].shape[0], ds[0].shape[1]])

    dcube[n] = np.copy(ds[0].values)

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

# we now have all the compartment we need, now plot them

# >>>>>>>>>>>>>>>> DISPLAY THE DATA

# setup generic mapbox display
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

# setup generic layout and for scatter data for EMPTY data
# this is displayed when something has not been clicked on
# if none is given, then a bug is given that means the plotting code
# cant figure out what to do.
normal_layout = go.Layout(
            xaxis={'title': "Timestep"},
            yaxis={'title': "Value"})

empty_data = [go.Scatter(x= time,
                    y= np.repeat(np.nan,len(time)),
                    mode='lines+markers',
                    name='Pixel',
                    marker={'color': 'rgba(0,150,150)'})]

# add the bits to the webpage
app.layout = html.Div( children=[
    
    html.H1(children='A demonstation on pulling out a pixels timeries',
            style = {'color': [0,141./256,165./256], 'textAlign': 'center'}),

    html.Div(id='labeler'),

    # set up the generic scatter display of the data itself
    html.Div(dcc.Graph(id='scatter_of_data',
                                 figure={'data': [data[1]],'layout': {'mapbox': mapbox}})),

    # put in an graph with no figure attribute
    html.Div(dcc.Graph(id='pixel_timeseries'))
])

# setup callbacks
@app.callback(
    dash.dependencies.Output(component_id = 'pixel_timeseries', component_property = 'figure'),
    [dash.dependencies.Input(component_id = 'scatter_of_data', component_property = 'clickData')])
def update(thing_to_print):

    # this branch is followed when nothing has been clicked on
    if thing_to_print is None:
        return {'data': empty_data, 'layout': normal_layout}

    # now pull out some of the data from the 3D cube we made before
    try:
        # pull out the lat and lon of the clicked point
        lat = thing_to_print['points'][0]['lat']
        lon = thing_to_print['points'][0]['lon']
        lat_ind = np.where(ds['y'].values == lat)[0][0]
        lon_ind = np.where(ds['x'].values == lon)[0][0]

        # make a new data object
        new_data = [go.Scatter(x= time,
                            y= dcube[:,lat_ind,lon_ind],
                            mode='lines+markers',
                            name='Pixel',
                            marker={'color': 'rgba(0,150,150)'})]

        new_insert = {'data': new_data, 'layout': normal_layout}

        # put it into the map
        return new_insert

    except:
        return {'data': [], 'layout': []}

@app.callback(
    dash.dependencies.Output(component_id='labeler', component_property='children'),
    [dash.dependencies.Input(component_id='scatter_of_data', component_property='clickData')])
def update_some_text(some_text):
    if some_text is None:
        return 'Please click on a data point in the window below.'
    else:
        try:
            lat = some_text['points'][0]['lat']
            lon = some_text['points'][0]['lon']

            return 'Selected data point is at %s latitude, %s longitude'%(lat,lon)
        except:
            return 'Please click on a data point within the dataset below'

if __name__ == '__main__':
    app.run_server(debug=True)
