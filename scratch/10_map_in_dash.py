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

def build_plot(dataframe, var, unc=False):

	if unc==False:
		cmin = float(dataframe[var].mean() - 2*dataframe[var].std())
		cmax = float(dataframe[var].mean() + 2*dataframe[var].std())
		colorscale='RdBu'
	else:
		cmin = 0
		cmax = float(dataframe[var].min() + 2*dataframe[var].std())
		colorscale='Viridis'

	return {'data': [
				 go.Scattermapbox(
				        lon=dataframe['longitude'].values,
				        lat=dataframe['latitude'].values,
				        hovertext=dataframe[var].values.astype(str),
				        hoverinfo='text',
				        mode='markers',
				        marker={
				            'size':10,
				            'color':df['lai'].values,
				            'symbol':'circle',
				            'cmin':cmin,
				            'cmax':cmax,
				            'colorscale': colorscale,
				            'showscale': True,
				            }
			            )
            ],
			'layout': go.Layout(
			    margin=dict(t=0,b=0,r=10,l=10),
			    autosize=True,
			    hovermode='closest',
			    showlegend=False,
			    mapbox=dict(
			        accesstoken=access_token,
			        bearing=0,
			        center=dict(
			            lat=np.mean(dataframe['latitude'].values),   
			            lon=np.mean(dataframe['longitude'].values)
			        ),
			        pitch=0,
			        zoom=13,
			        style='light'
			    ),
			)
        }




app = dash.Dash(__name__)

markdown_text = '''
Test of plotting surface raster plot in a dash.
'''

access_token='pk.eyJ1IjoiYmV0aGFucGVya2lucyIsImEiOiJpZ1lWQXlzIn0.comSgcNvpNUaLuXE0EOc8A'

input_file = "../data/lai_A2017171.tif"
input_unc_file = "../data/lai_A2017171_unc.tif"

tmp_vrt = 'outfile.vrt'

# Define data plot
df = build_df(input_file)
data_plot = build_plot(df, 'lai')


# Define uncertainty plot
df_unc = build_df(input_unc_file)
unc_plot = build_plot(df_unc, 'lai', unc=True)

# Setup page
app.layout = html.Div([
	html.H1("Test 10: Map in a dashboard"),
	dcc.Markdown(children=markdown_text),
	html.Div(style={'width': '40%', 'float':'left', 'display':'inline-block'}, children=[
		dcc.Graph(id='the-map', figure=data_plot),
		]),
	html.Div(style={'width': '40%', 'float':'left', 'display':'inline-block'}, children=[
		dcc.Graph(id='the-unc-map', figure=unc_plot),
		]),

])






if __name__ == '__main__':
    app.run_server(debug=True)