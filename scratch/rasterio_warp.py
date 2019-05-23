import gdal
import xarray as xr
import matplotlib.pyplot as plt

input_file = "../data/cw_A2017171.tif"

tmp_vrt = 'outfile.vrt'

gdal.Warp(
	srcDSOrSrcDSTab=input_file,
	destNameOrDestDS='outfile.vrt',
	format='VRT',
	dstSRS = 'EPSG:4326',
	)

ds = xr.open_rasterio(tmp_vrt)
ds.plot()
plt.show()

print('\n\n=========================\n\n')
print(ds)
print(ds.max())
print('\n\n=========================\n\n')

dp = xr.open_rasterio(input_file)

print(dp)
print(dp.max())
dp.plot()
plt.show()
