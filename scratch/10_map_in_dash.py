import gdal
import xarray as xr
import matplotlib.pyplot as plt
import plotly.plotly as py
import plotly.offline as py_off
import plotly.graph_objs as go
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html


def build_df(filename):
	# convert to lat/lon
	gdal.Warp(
	    srcDSOrSrcDSTab=filename,
	    destNameOrDestDS='outfile.vrt',
	    format='VRT',
	    dstSRS = 'EPSG:4326')

	# open the data set
	ds = xr.open_rasterio(tmp_vrt)

	# convert it to a 2 dimensional dataframe
	df = ds.to_dataframe('lai')

	# Extract lat/lon to seperate columns
	df['latitude'] = df.index.get_level_values('y')
	df['longitude'] = df.index.get_level_values('x')

	return df

app = dash.Dash()

markdown_text = '''
Test of plotting surface raster plot in a dash.
'''

access_token='pk.eyJ1IjoiYmV0aGFucGVya2lucyIsImEiOiJpZ1lWQXlzIn0.comSgcNvpNUaLuXE0EOc8A'

input_file = "../data/lai_A2017171.tif"
input_unc_file = "../data/lai_A2017171_unc.tif"

tmp_vrt = 'outfile.vrt'

name = 'lai'

# # convert to lat/lon
# gdal.Warp(
#     srcDSOrSrcDSTab=input_file,
#     destNameOrDestDS='outfile.vrt',
#     format='VRT',
#     dstSRS = 'EPSG:4326')

# # open the data set
# ds = xr.open_rasterio(tmp_vrt)

# # convert it to a 2 dimensional dataframe
# df = ds.to_dataframe('lai')

# # Extract lat/lon to seperate columns
# df['latitude'] = df.index.get_level_values('y')
# df['longitude'] = df.index.get_level_values('x')

df = build_df(input_file)

# Define data plot
data_plot = {'data': [
				 go.Scattermapbox(
				        lon=df['longitude'].values,
				        lat=df['latitude'].values,
				        hovertext=df['lai'].values.astype(str),
				        hoverinfo='text',
				        mode='markers',
				        marker={
				            'size':10,
				            'color':df['lai'].values,
				            'symbol':'circle',
				            'cmin':float(df['lai'].mean() - 2*df['lai'].std()),
				            'cmax':float(df['lai'].mean() + 2*df['lai'].std())}
			            )
            ],
			'layout': go.Layout(
			    margin=dict(t=0,b=0,r=0,l=0),
			    autosize=True,
			    hovermode='closest',
			    showlegend=False,
			    mapbox=dict(
			        accesstoken=access_token,
			        bearing=0,
			        center=dict(
			            lat=np.mean(df['latitude'].values),   
			            lon=np.mean(df['longitude'].values)
			        ),
			        pitch=0,
			        zoom=13,
			        style='light'
			    ),
			)
        }

# Define uncertainty plot
unc_plot = {'data': [
				 go.Scattermapbox(
				        lon=df['longitude'].values,
				        lat=df['latitude'].values,
				        hovertext=df['lai'].values.astype(str),
				        hoverinfo='text',
				        mode='markers',
				        marker={
				            'size':10,
				            'color':df['lai'].values,
				            'symbol':'circle',
				            'cmin':float(df['lai'].mean() - 2*df['lai'].std()),
				            'cmax':float(df['lai'].mean() + 2*df['lai'].std())}
			            )
            ],
			'layout': go.Layout(
			    margin=dict(t=0,b=0,r=0,l=0),
			    autosize=True,
			    hovermode='closest',
			    showlegend=False,
			    mapbox=dict(
			        accesstoken=access_token,
			        bearing=0,
			        center=dict(
			            lat=np.mean(df['latitude'].values),   
			            lon=np.mean(df['longitude'].values)
			        ),
			        pitch=0,
			        zoom=13,
			        style='light'
			    ),
			)
        }

# Setup page
app.layout = html.Div([
	html.H1("Test 10: Map in a dashboard"),
	dcc.Markdown(children=markdown_text),
    dcc.Graph(id='the-map',
        figure=data_plot),
])






if __name__ == '__main__':
    app.run_server(debug=True)