import gdal
import xarray as xr
import matplotlib.pyplot as plt
import plotly.plotly as py
import plotly.offline as py_off
from plotly.graph_objs import *

input_file = "../data/lai_A2017171.tif"

tmp_vrt = 'outfile.vrt'

# convert to lat/lon
gdal.Warp(
    srcDSOrSrcDSTab=input_file,
    destNameOrDestDS='outfile.vrt',
    format='VRT',
    dstSRS = 'EPSG:4326')

# open the data set
ds = xr.open_rasterio(tmp_vrt)


# take  subset around some interesting bits for speed
ds = ds.isel(x=range(50,100),y=range(125,175))

# convert it to a 2 dimensional dataframe
df = ds.to_dataframe('lai')

# pull out the usefull bits from the nested index
# this is so the data knows where to put itself
df['latitude'] = df.index.get_level_values('y')
df['longitude'] = df.index.get_level_values('x')

data = []

data.append(
    Scattermapbox(
        lon=df['longitude'].values,
        lat=df['latitude'].values,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=18,
            color=df['lai'].values)))
        
layout = Layout(
    margin=dict(t=0,b=0,r=0,l=0),
    autosize=True,
    hovermode='closest',
    showlegend=False,
    mapbox=dict(
        accesstoken=access_token,
        bearing=0,
        center=dict(
            lat=np.mean(df_no_nan['latbin'].values),
            lon=np.mean(df_no_nan['lonbin'].values)
        ),
        pitch=0,zoom=15,
        style='light'
    ),
)

plotly.offline.init_notebook_mode(connected=False)
# and plot it
plotly.offline.iplot(fig)