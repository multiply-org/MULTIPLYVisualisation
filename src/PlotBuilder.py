import datetime as dt
import numpy as np
import pandas as pd

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

from src.DataHandling import DataHandling


class Plots:

    def __init__(self, data_directory):

        self.dh = DataHandling(data_directory)

        self.access_token = 'pk.eyJ1IjoiYWxleGNvcm5lbGl1cyIsImEiOiJjandhcXZ2ZnMwYnB0NDlzNnJyYXF2NGh5In0.dOemdsmJJfkte6eeoBrQbQ'

    def generate_parameter_dropdown(self, name):
        """
        Build the 'select parameter' dropdown
        :return:
        """

        params = self.dh.get_available_parameters()

        dropdown = html.Div(
            dcc.Dropdown(
                id=name,
                options=[{'label': i, 'value': i} for i in params],),
            style={'width': '100px', 'display': 'inline-block'})
        if name == 'parameter_select2':
            dropdown = html.Div(
                dcc.Dropdown(
                    id=name,
                    options=[{'label': i, 'value': i} for i in params],
                disabled=True),
                style={'width': '100px', 'display': 'inline-block'})

        return dropdown

    def slider(self, param):
        """
        Create the slider which displays the timesteps of the data
        :return:
        """
        timesteps = self.dh.get_timesteps(param)

        div_value = len(timesteps)//4

        slider = dcc.Slider(
            id='time-slider',
            min=timesteps[0].value,
            max=timesteps[-1].value,
            value=timesteps[0].value,
            marks={
                timestep.value: timestep.strftime("%d-%m-%Y")
                for timestep in timesteps
                if timesteps.index(timestep) % div_value == 0
            },
            step=timesteps[1].value-timesteps[0].value,
            dots=True
        )

        return slider

    def update_maps(self, timestamp, param, maxmin):
        """
        Use the timestamp and the parameter to update hte maps
        :param timestamp:
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
        core_map = self.create_map(df, vis_stats['core'], maxmin)
        unc_map = self.create_map(df, vis_stats['unc'], maxmin, unc=True)

        return core_map, unc_map

    def update_unc_map(self, timestamp, param, maxmin):

        dtime = pd.Timestamp(timestamp).to_pydatetime()

        df = self.dh.get_timestep(param, time=dtime)

        vis_stats = self.dh.get_vis_stats(param)

        unc_map = self.create_map(df, vis_stats['core'], maxmin)

        return unc_map

    def get_data_and_colorscale(self, df, vis_stats, unc=False):
        if not unc:
            data = df['mean']

            if (vis_stats['mean'] - vis_stats['std'] < vis_stats['min'] or
                    vis_stats['mean'] + vis_stats['std'] > vis_stats['min']):

                # Set min and max for colourscales based on min and max
                cmin = float(vis_stats['min'])
                cmax = float(vis_stats['max'])

            else:

                # Set min and max colourscales based on mean and std
                cmin = float(vis_stats['mean'] - 2 * vis_stats['std'])
                cmax = float(vis_stats['mean'] + 2 * vis_stats['std'])

            colorscale = 'Viridis'
        else:

            data = (df['mean'] - df['min']).abs()

            cmin = 0.0
            cmax = float(vis_stats['max'])

            colorscale = 'Hot'
        return colorscale, data, cmin, cmax

    def create_map(self, df, vis_stats, maxmin, unc=False):
        """
        Build the map
        """
        if maxmin is None:
            if not unc:

                params = self.get_data_and_colorscale(df, vis_stats)
                colorscale = params[0]
                data = params[1]
                cmin = params[2]
                cmax = params[3]
            else:

                params = self.get_data_and_colorscale(df, vis_stats, unc=True)
                colorscale = params[0]
                data = params[1]
                cmin = params[2]
                cmax = params[3]

        elif maxmin is not None:

            if not unc:
                if maxmin[0] != 0.0 and maxmin[1] != 0.0:

                    data = df['mean']
                    cmin = maxmin[0]
                    cmax = maxmin[1]
                    colorscale = 'Viridis'

                elif maxmin[0] != 0:

                    params = self.get_data_and_colorscale(df, vis_stats)
                    colorscale = params[0]
                    data = params[1]
                    cmin = maxmin[0]
                    cmax = params[3]

                elif maxmin[1] != 0:

                    params = self.get_data_and_colorscale(df, vis_stats)
                    colorscale = params[0]
                    data = params[1]
                    cmin = params[2]
                    cmax = maxmin[1]

                else:

                    params = self.get_data_and_colorscale(df, vis_stats,
                                                          unc=False)
                    colorscale = params[0]
                    data = params[1]
                    cmin = params[2]
                    cmax = params[3]

            else:
                if maxmin[2] != 0 and maxmin[3] != 0:
                    data = (df['mean'] - df['min']).abs()

                    cmin = maxmin[2]
                    cmax = maxmin[3]

                elif maxmin[2] != 0.0:
                    data = (df['mean'] - df['min']).abs()

                    cmin = maxmin[2]
                    cmax = float(vis_stats['max'])

                elif maxmin[3] != 0.0:
                    data = (df['mean'] - df['min']).abs()

                    cmin = 0.0
                    cmax = maxmin[3]

                else:
                    data = (df['mean'] - df['min']).abs()

                    cmin = 0.0
                    cmax = float(vis_stats['max'])

                colorscale = 'Hot'

        if data is not None:
            data = go.Scattermapbox(
                lon=df.index.get_level_values('longitude').values,
                lat=df.index.get_level_values('latitude').values,
                hovertext=data.astype(str),
                hoverinfo='text',
                mode='markers',
                marker={
                    'size': 10,
                    'color': data,
                    'symbol': 'circle',
                    'cmin': cmin,
                    'cmax': cmax,
                    'colorscale': colorscale,
                    'showscale': True,
                }
            )

            layout = go.Layout(
                margin=dict(t=0, b=0, r=10, l=10),
                height=350,
                width=620,
                autosize=False,
                # hovermode='closest',
                # showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                mapbox=dict(
                     accesstoken=self.access_token,
                     bearing=0,
                     center=dict(
                         lat=np.mean(
                             df.index.get_level_values('latitude').values),
                         lon=np.mean(
                             df.index.get_level_values('longitude').values)
                     ),
                     pitch=0,
                     zoom=13,
                     style='light'
                ),
                uirevision='yes'
            )
        return {'data': [data], 'layout': layout}

    def create_timeseries(self, param, lat, lon, area_data, area=False):
        """
        :param param:
        :param lat:
        :param lon:
        :return:
        """

        vis_stats = self.dh.get_vis_stats(param)

        if lat and lon:

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

        elif area:
            df = self.dh.get_timesteps(param)

            time = [pd.to_datetime(t).strftime("%d-%m-%Y") for t in
                    df]

            mean_line = go.Scatter(
                x=time,
                y=area_data[0],
                mode='lines+markers',
                name='mean',
                marker={'color': 'rgba(0,150,150)'},
                error_y=dict(
                    type='data',
                    symmetric=False,
                    array=np.array(area_data[2].where(
                        np.isfinite(area_data[2]), np.nan) -
                        area_data[0].where(np.isfinite(area_data[0]), np.nan)),
                    arrayminus=np.array(np.array(area_data[0], dtype=float) -
                        area_data[1].where(np.isfinite(area_data[1]), np.nan))
                )
            )
            std_line = go.Scatter(
                x=time,
                y=np.array(area_data[0].where(np.isfinite(area_data[0]), np.nan) -
                  vis_stats['core']['std'].item()),
                mode='lines+markers',
                name='standard deviation',
                marker={'color': 'red',
                        'size': 3.5},
                error_y=None,
            )
            std_line2 = go.Scatter(
                x=time,
                y=np.array(area_data[0].where(np.isfinite(area_data[0]), np.nan)
                           + vis_stats['core']['std'].item()),
                mode='lines+markers',
                name='standard deviation',
                marker={'size': 3.5,
                         'color': 'green'},
                error_y=None
            )
            data = [mean_line, std_line, std_line2]

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
            yaxis={'title': param},
            width=1500,
            height=277,
            autosize=True,  # False,
            paper_bgcolor='rgba(0,0,0,0)',
            margin=go.layout.Margin(
                l=40,
                r=0,
                b=40,
                t=15,
                pad=4)
            )

        return {'data': data, 'layout': layout}

    def get_data(self, param, lats, lons):

        df = self.dh.get_stats(param, lats, lons)
        timesteps = self.dh.get_timesteps(param)

        return df,timesteps

    def create_csv_string(self, param, lat, lon):
        """
        :param param:
        :param lat:
        :param lon:
        :return:
        """

        df = self.dh.get_timeseries(param, lat, lon)
        div_value= len(df)//8

        df = df.iloc[:div_value]

        csv_string = df.to_csv(encoding='utf-8')

        return csv_string
