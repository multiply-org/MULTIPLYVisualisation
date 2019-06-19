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
import datetime as dt

import dash
from dash.dependencies import Input, Output, State

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
        Output(component_id='slider-container', component_property='children'),
        [Input('select', 'n_clicks')],
        [State(component_id='parameter_select', component_property='value')])
    def initialise_slider(n_clicks, parameter):
        if n_clicks:

            # Build the slider
            slider = app.plotter.build_slider(parameter)

            return slider

        else:
            pass

    @staticmethod
    @app.callback(
        Output(component_id='pixel_timeseries', component_property='figure'),
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

            return timeseries_plot

        else:

            return {}


    @staticmethod
    @app.callback([Output(component_id='core-map', component_property='figure'),
                   Output(component_id='unc-map', component_property='figure')],
                  [Input('time-slider', 'value')],
                  [State(component_id='parameter_select',
                         component_property='value')])
    def update_maps(timestamp, parameter):
        """

        :param timestamp:
        :param parameter:
        :return:
        """

        maps = app.plotter.update_maps(timestamp, parameter)

        return maps

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
        return dt.datetime.fromtimestamp(selected_time).strftime("%Y-%m-%d")


if __name__ == "__main__":

    MultiplyVis()