#######################################################
#
# MultiplyVis.py
# Orchestrator class for the multiply Visualisation
#
# Created on:      12-Jun-2019
# Original author: Bethan Perkins
#
#######################################################
import os
import pandas as pd
import urllib.parse
import numpy as np

import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

from src.PlotBuilder import Plots
from src.Layout import Layout


# Instantiate the app on import
app = dash.Dash(__name__)

server = app.server
app.config['suppress_callback_exceptions'] = True
app.plotter = None # create a blank space for the plotter, once we have
                    # a directory to work with

class MultiplyVis:
    """
    This is the wrapper/orchestrator class for the MULTIPLY visualisation
    """
    def __init__(self, data_directory=os.path.abspath('../data/')):
        """
        This should start up on initialisation.

        """
        # Add the PlotBuilder class on to the 'app' object. It's not pretty, but
        # it works as a way of passing the directory/plotting methods to the
        # callbacks

        app.plotter = Plots(data_directory)

        app.layout = Layout.index(app.plotter)

        app.run_server(debug=True)

    @staticmethod
    @app.callback(
        Output(component_id='slider_container', component_property='children'),
        [Input('select', 'n_clicks')],
        [State(component_id='parameter_select', component_property='value')])
    def initialise_slider(n_clicks, parameter):
        if n_clicks:

            # Build the slider
            slider = app.plotter.slider(parameter)

            return slider

        else:
            pass

    @staticmethod
    @app.callback(
        [Output(component_id='pixel_timeseries', component_property='figure'),
         Output('download-link', 'href')],
        [Input(component_id='core-map', component_property='clickData'),
         Input(component_id='unc-map', component_property='clickData')],
        [State(component_id='parameter_select', component_property='value')])
    def update_timeseries(location_info1, location_info2, parameter):
        """

        :param location_info:
        :return:
        """

        # Isolate the input which has triggered this callback
        trigger = dash.callback_context.triggered[0]

        if trigger['value']:

            # Update latitude and longitude from map click
            latitude = trigger['value']['points'][0]['lat']
            longitude = trigger['value']['points'][0]['lon']

            # Create the timeseries plot
            timeseries_plot = app.plotter.create_timeseries(
                parameter, latitude, longitude)

            # Get the csv string
            csv_string_base = app.plotter.create_csv_string(parameter,
                                                            latitude, longitude)
            # Convert this into a csv-like html string
            csv_string = "data:text/csv;charset=utf-8," + \
                         urllib.parse.quote(csv_string_base)

            return timeseries_plot, csv_string

        else:

            layout = go.Layout(
                xaxis={'ticks': '', 'showticklabels': False,
                       'zeroline': False, 'showgrid':False},
                yaxis={'ticks': '', 'showticklabels': False,
                       'zeroline': False, 'showgrid':False},
                width=1265,
                height=271,
                autosize=False,
                margin=go.layout.Margin(
                    l=80,
                    r=0,
                    b=80,
                    t=30,
                    pad=4)
            )

            dummy_data = [go.Scatter(
                x=np.arange(5),
                y=np.arange(5)*np.nan
            )]

            return {'data': dummy_data, 'layout': layout}

    # @staticmethod
    # @app.callback([Output(component_id='core-map', component_property='figure'),
    #                Output(component_id='unc-map', component_property='figure')],
    #               [Input('time-slider', 'value')],
    #               [State('parameter_select', 'value')])
    # def update_maps(timestamp, parameter):
    #     """
    #
    #     :param timestamp:
    #     :param parameter:
    #     :return:
    #     """
    #
    #     maps = app.plotter.update_maps(timestamp, parameter)
    #
    #     return maps

    @staticmethod
    @app.callback([Output(component_id='core-map', component_property='figure'),
                   Output(component_id='unc-map', component_property='figure')],
                  [Input('time-slider', 'value'),
                   Input('pixel_timeseries', 'clickData')],
                  [State('parameter_select', 'value')])
    def update_maps(input_plot, input_slider, parameter):
        """
        Update the maps in response to click on the slider or the timeseries
        :param input_plot:
        :param input_slider:
        :return:
        """

        trigger = dash.callback_context.triggered[0]

        if trigger['value']:

            if isinstance(trigger['value'], int):

                # Extract timestamp from slider
                timestamp = trigger['value']

            else:

                # Extract timestamp from timeseries plot
                timestamp = pd.Timestamp(trigger['value']['points'][0]['x'])


            maps = app.plotter.update_maps(timestamp, parameter)

            return maps

        else:

            dummy_data = [go.Scattermapbox(
            lon=[],
            lat=[])]

            access_token = 'pk.eyJ1IjoiYmV0aGFucGVya2lucyIsI' \
                           'mEiOiJpZ1lWQXlzIn0.comSgcNvpNUaLuXE0EOc8A'

            layout = go.Layout(
            margin=dict(t=0, b=0, r=10, l=10),
            autosize=False,
            height=640,
            width=640,
            hovermode='closest',
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            mapbox=dict(
                accesstoken=access_token,
                bearing=0,
                pitch=0,
                style='light'
            )
        )
            return {'data': dummy_data,'layout': layout},\
                   {'data': dummy_data,'layout': layout}

    @staticmethod
    @app.callback(
        Output('time-slider', 'value'),
        [Input('pixel_timeseries', 'clickData')])
    def update_markup(selected_time):
        """
        Update the slider when changing time via the plot
        :param selected_time:
        :return:
        """

        trigger = dash.callback_context.triggered[0]

        if trigger['value']:

            timestamp = pd.Timestamp(trigger['value']['points'][0]['x'])

            return timestamp.value
        else:
            pass

    @staticmethod
    @app.callback(
        Output('markdown', 'children'),
        [Input('time-slider', 'value')])
    def update_markup(selected_time):
        """
        Post the date of the marker to the markdown string to make sure we're seeing time updating
        :param selected_time:
        :return:
        """

        trigger = dash.callback_context.triggered[0]

        if trigger['value']:

            date = pd.Timestamp(selected_time).to_pydatetime().strftime("%Y-%m-%d")

            return f"Date: {date}"

        else:

            pass


if __name__ == "__main__":

    MultiplyVis()

    #MultiplyVis(os.path.abspath('../data_2/kafkaout_Barrax_Q1_noprior_S2/'))