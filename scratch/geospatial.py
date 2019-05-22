# coding=utf-8
import dash
import dash_core_components as dcc
import dash_html_components as html

import xarray as xr

# use tutorial dataset
ds = xr.tutorial.load_dataset('rasm')

# convert to dataframe
df = ds.Tair.to_dataframe()

# clean out nans
df.dropna(axis=0, subset=['Tair'], inplace=True)

# subset on a date
df_sub = df.loc['1980-09-16']

print(df_sub)