import datetime as dt
import numpy as np
import pandas as pd

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from src.DataHandling import DataHandling

class Plots:

    def __init__(self, data_directory):

        self.dh = DataHandling(data_directory)


        self.access_token = 'pk.eyJ1IjoiYmV0aGFucGVya2lucyIsI' \
                            'mEiOiJpZ1lWQXlzIn0.comSgcNvpNUaLuXE0EOc8A'

    def generate_parameter_dropdown(self):
        """
        Build the 'select parameter' dropdown
        :return:
        """

        params = self.dh.get_available_parameters()

        dropdown  = html.Div(
            dcc.Dropdown(
                id='parameter_select',
                options=[{'label': i, 'value': i} for i in params],),
            style={'width':'100px', 'display': 'inline-block'})

        return dropdown

    def slider(self, param):
        """
        Create the slider which displays the timesteps of the data
        :return:
        """

        timesteps = self.dh.get_timesteps(param)

        slider = dcc.Slider(
            id='time-slider',
            min=timesteps[0].value,
            max=timesteps[-1].value,
            value=timesteps[0].value,
            marks={
                timestep.value: timestep.strftime("%d-%m-%Y")
                for timestep in timesteps},
            step=None,
        )

        return slider

    def update_maps(self, timestamp, param):
        """
        Use the timestep and the parameter to update hte maps
        :param timestep:
        :param param:
        :return:
        """
        # Convert timestamp to datetime
        dtime = pd.Timestamp(timestamp).to_pydatetime()

        # Extract this data
        df = self.dh.get_timestep(param, time=dtime)

        # Extract the visulaisation statistics
        vis_stats = self.dh.get_vis_stats(param)

        # Build the maps
        core_map = self.create_map(df, vis_stats['core'])
        unc_map = self.create_map(df, vis_stats['unc'], unc=True)

        return core_map, unc_map

    def create_map(self, df, vis_stats, unc=False):
        """
        Build the map
        """

        cmin = vis_stats['mean'] - 2 * vis_stats['std']
        cmax = vis_stats['mean'] + 2 * vis_stats['std']

        if not unc:
            data = df['mean'].values
        else:
            data = df['max'].values - df['min'].values

        #
        #
        # if not unc:
        #     data = df['mean'].values
        #     v_elements = {
        #         'cmin': float(df['mean'].mean() - 2 * df['mean'].std()),
        #         'cmax': float(df['mean'].mean() + 2 * df['mean'].std()),
        #         'colorscale': 'RdBu',
        #     }
        # else:
        #     data = df['max'].values - df['min'].values
        #     # todo: clean this up
        #     v_elements = {
        #         'cmin': 0,
        #         'cmax': float(df['mean'].min() + 2 * df['mean'].std()),
        #         'colorscale': 'Viridis',
        #     }

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
                'cmin': cmin,
                'cmax': cmax,
                #'colorscale': v_elements['colorscale'],
                'showscale': True,
            }
        )

        layout = go.Layout(
            margin=dict(t=0, b=0, r=10, l=10),
            autosize=True,
            hovermode='closest',
            showlegend=False,
            mapbox=dict(
                accesstoken=self.access_token,
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

    def create_timeseries(self, param, lat, lon):
        """

        :param df:
        :return:
        """

        df = self.dh.get_timeseries(param, lat, lon)

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
                array=df['max'] - df['mean'],
                arrayminus=df['mean'] - df['min']
            )
        )

        data = [mean_line]

        # maxmin_fill = go.Scatter(
        #     x=time + time[::-1],  # time forwards and then backwards
        #     y=pd.concat([df['max'], df['min'][::-1]]),
        #     fill='tozerox',
        #     fillcolor='rgba(0,150,150, 0.5)',
        #     line=dict(color='rgba(0,150,150, 0)'),
        #     name='Range')
        #
        # data = [mean_line, maxmin_fill]

        layout = go.Layout(
            xaxis={'title': "Timestep"},
            yaxis={'title': param})

        return {'data': data, 'layout': layout}