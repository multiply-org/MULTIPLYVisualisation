# coding=utf-8
import dash
import dash_core_components as dcc
import dash_html_components as html

import xarray as xr

# Open a MULTIPLY dataset
ds = xr.open_rasterio("../data/lai_A2017156.tif")

# convert to dataframe
#df = ds.to_dataframe(name='LAI')


# # use tutorial dataset
# ds = xr.tutorial.load_dataset('rasm')

# # convert to dataframe
# df = ds.Tair.to_dataframe()

# # clean out nans
# df.dropna(axis=0, subset=['Tair'], inplace=True)

# # subset on a date
# df_sub = df.loc['1980-09-16']

print(ds)



def in_latlon(da):
	"""
	https://anaconda.org/jhamman/rasterio_to_xarray/notebook
	"""

    if 'crs' in da.attrs:
        proj = pyproj.Proj(da.attrs['crs'])
        x, y = np.meshgrid(da['x'], da['y'])
        proj_out = pyproj.Proj("+init=EPSG:4326", preserve_units=True)
        xc, yc = transform_proj(proj, proj_out, x, y)
        coords = dict(y = da['y'], x=da['x'])
        dims = ('y', 'x')
        
        da.coords['latitude'] = xr.DataArray(yc, coords=coords, dims=dims, name='latitude',
                                             attrs={'units': 'degrees_north', 'long_name': 'latitude', 'standard_name': 'latitude'})
        da.coords['longitude'] = xr.DataArray(xc, coords=coords, dims=dims, name='latitude',
                                             attrs={'units': 'degrees_east', 'long_name': 'longitude', 'standard_name': 'longitude'})
    
    return da