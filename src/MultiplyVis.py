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
import datetime as dt

import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

from src.PlotBuilder import Plots
from src.Layout import Layout


# Instantiate the app on import, pass external stylesheets from layout
app = dash.Dash(__name__)  # external_stylesheets=Layout.external_stylesheets)

server = app.server
app.config['suppress_callback_exceptions'] = True
app.plotter = None  # create a blank space for the plotter, once we have
# a directory to work with


class MultiplyVis:
    """
    This is the wrapper/orchestrator class for the MULTIPLY visualisation
    """
    def __init__(self, data_directory=os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/'))):
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
        if n_clicks and parameter is not None:

            # Build the slider
            slider = app.plotter.slider(parameter)

            return slider

        else:
            pass

    @staticmethod
    @app.callback(
        [Output(component_id='pixel_timeseries', component_property='figure'),
         Output('download_link', 'href'),
         Output('download_button', 'style')],
        [Input(component_id='core-map', component_property='clickData'),
         Input(component_id='unc-map', component_property='clickData'),
         Input('core-map', 'selectedData'),
         Input('unc-map', 'selectedData')],
        [State(component_id='parameter_select', component_property='value'),
         State(component_id='parameter_select2', component_property='value'),
         State('dropdown_container2', 'style')])
    def update_timeseries(location_info1, location_info2, core_selected_data,
                          unc_selected_data, parameter, parameter2,
                          dropdown_state):
        """
        Updates time series to show the single time series or works out the
        mean for an area and shows the standard deviation
        :param location_info1:
        :param location_info2:
        :param core_selected_data:
        :param unc_selected_data:
        :param parameter:
        :param parameter2:
        :param dropdown_state:
        :return:
        """

        # Isolate the input which has triggered this callback
        trigger = dash.callback_context.triggered[0]

        if trigger['prop_id'] == 'core-map.clickData' or \
                trigger['prop_id'] == 'unc-map.clickData':
            # Update latitude and longitude from map click

            latitude = trigger['value']['points'][0]['lat']
            longitude = trigger['value']['points'][0]['lon']

            # Create the timeseries plot

            if (trigger['prop_id'] == 'core-map.clickData' or parameter2 is
                None) or dropdown_state['visibility'] == 'none' or \
                    dropdown_state['visibility'] == 'hidden':

                timeseries_plot = app.plotter.create_timeseries(
                    parameter, latitude, longitude, 0)

            elif trigger['prop_id'] == 'unc-map.clickData' and \
                    dropdown_state['visibility'] == 'visible':

                timeseries_plot = app.plotter.create_timeseries(
                     parameter2, latitude, longitude, 0)

            # Get the csv string
            csv_string_base = app.plotter.create_csv_string(parameter,
                                                            latitude, longitude)
            # Convert this into a csv-like html string
            csv_string = "data:text/csv;charset=utf-8," + \
                         urllib.parse.quote(csv_string_base)

            return timeseries_plot, csv_string, {'display': 'block'}

        elif core_selected_data is not None or unc_selected_data is not None:

            if trigger['prop_id'] == 'core-map.selectedData':

                lats = [core_selected_data['range']['mapbox'][0][1],
                        core_selected_data['range']['mapbox'][1][1]]
                if core_selected_data['range']['mapbox'][0][0] < \
                        core_selected_data['range']['mapbox'][1][0]:
                    lons = [core_selected_data['range']['mapbox'][0][0],
                            core_selected_data['range']['mapbox'][1][0]]
                else:
                    lons = [core_selected_data['range']['mapbox'][1][0],
                            core_selected_data['range']['mapbox'][0][0]]

                return_vals = app.plotter.get_data(parameter, lats, lons)
            elif trigger['prop_id'] == 'unc-map.selectedData':

                lats = [unc_selected_data['range']['mapbox'][0][1],
                        unc_selected_data['range']['mapbox'][1][1]]
                if unc_selected_data['range']['mapbox'][0][0]\
                        > unc_selected_data['range']['mapbox'][1][0]:
                    lons = [unc_selected_data['range']['mapbox'][1][0],
                            unc_selected_data['range']['mapbox'][0][0]]
                else:
                    lons = [unc_selected_data['range']['mapbox'][0][0],
                            unc_selected_data['range']['mapbox'][1][0]]

                if parameter2 is not None:
                    return_vals = app.plotter.get_data(parameter2, lats, lons)
                    df = return_vals[0]

                    means = df.where(np.isfinite(df['mean']), np.nan).mean(
                        level=2, skipna=True)['mean']
                    mins = df.where(np.isfinite(df['min']), np.nan).mean(
                        level=2, skipna=True)['min']
                    maxs = df.where(np.isfinite(df['max']), np.nan).mean(
                        level=2, skipna=True)['max']

                    area_data = [means, mins, maxs]
                    timeseries_plot = app.plotter.create_timeseries(parameter2,
                                                                    0, 0,
                                                                    area_data,
                                                                    area=True)

                    csv_string_base = app.plotter.create_csv_string(parameter2,
                                                                    lats[0],
                                                                    lons[0])
                    csv_string = "data:text/csv;charset=utf-8," + \
                                 urllib.parse.quote(csv_string_base)
                    return timeseries_plot, csv_string, {'display': 'block'}
                elif parameter2 is None:
                    return_vals = app.plotter.get_data(parameter, lats, lons)
            else:
                layout = go.Layout(
                    xaxis={'ticks': '', 'showticklabels': False,
                           'zeroline': False, 'showgrid': False},
                    yaxis={'ticks': '', 'showticklabels': False,
                           'zeroline': False, 'showgrid': False},
                    width=1500,
                    height=339,
                    autosize=True,  # False
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

                return {'data': dummy_data, 'layout': layout}, "", \
                       {'display': 'none'}
                pass


            df = return_vals[0]

            means = df.where(np.isfinite(df['mean']), np.nan).mean(
                level=2, skipna=True)['mean']
            mins = df.where(np.isfinite(df['min']), np.nan).mean(
                level=2, skipna=True)['min']
            maxs = df.where(np.isfinite(df['max']), np.nan).mean(
                level=2, skipna=True)['max']

            area_data = [means, mins, maxs]
            timeseries_plot = app.plotter.create_timeseries(parameter, 0, 0,
                                                            area_data,
                                                            area=True)

            csv_string_base = app.plotter.create_csv_string(parameter,
                                                            lats[0], lons[0])
            csv_string = "data:text/csv;charset=utf-8," + \
                         urllib.parse.quote(csv_string_base)
            return timeseries_plot, csv_string, {'display': 'block'}

        else:

            layout = go.Layout(
                xaxis={'ticks': '', 'showticklabels': False,
                       'zeroline': False, 'showgrid': False},
                yaxis={'ticks': '', 'showticklabels': False,
                       'zeroline': False, 'showgrid': False},
                width=1500,
                height=339,
                autosize=True,  # False
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

            return {'data': dummy_data, 'layout': layout}, "", \
                   {'display': 'none'}

    @staticmethod
    @app.callback([Output(component_id='core-map', component_property='figure'),
                   Output(component_id='unc-map', component_property='figure'),
                   Output('cmax', 'value'),
                   Output('cmin', 'value'),
                   Output('unc_cmax', 'value'),
                   Output('unc_cmin', 'value')],
                  [Input('time-slider', 'value'),
                   Input('select2', 'n_clicks'),
                   Input('colorscale_update', 'n_clicks'),
                   Input('core-map', 'relayoutData'),
                   Input('unc-map', 'relayoutData')],
                  [State('parameter_select', 'value'),
                   State('parameter_select2', 'value'),
                   State('time-slider', 'value'),
                   State('cmin', 'value'),
                   State('cmax', 'value'),
                   State('unc_cmin', 'value'),
                   State('unc_cmax', 'value'),
                   State('core-map', 'figure'),
                   State('unc-map', 'figure')
                   ])
    def update_maps(input_slider, n_clicks, n_clicks2, core_relayout_data,
                    unc_relayout_data, parameter, parameter2, time_slider,
                    cmin, cmax, unc_cmin, unc_cmax, core_map, unc_map):
        """
        Update the maps in response to click on the slider or the timeseries or
        button on the second dropdown
        this also prevents it from updating maps if there is no parameter or
        parametet2 as that causes errors
        :param input_slider:
        :param n_clicks:
        :param n_clicks2:
        :param core_relayout_data:
        :param unc_relayout_data:
        :param parameter:
        :param parameter2:
        :param time_slider:
        :param cmin:
        :param cmax:
        :param unc_cmin:
        :param unc_cmax:
        :param core_map:
        :param unc_map:
        :return:
        """

        trigger = dash.callback_context.triggered[0]
        # Program does not take into account the max min if the colorscale
        # buttton is not clicked so maxmin is set to none if it is not used

        access_token = 'pk.eyJ1IjoiYWxleGNvcm5lbGl1cyIsImEiOiJjandhcXZ2ZnMwYnB0NDlzNnJyYXF2NGh5In0.dOemdsmJJfkte6eeoBrQbQ'

        if parameter is None:
            # gives dummy data if it is not given any parameter
            dummy_data = [go.Scattermapbox(
                lon=[],
                lat=[])]

            layout = go.Layout(
                margin=dict(t=10, b=10, r=10, l=10),
                autosize=True,
                height=350,
                width=620,
                hovermode='closest',
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                mapbox=dict(
                    accesstoken=access_token,
                    bearing=0,
                    pitch=0,
                    style='light'
                ),
                uirevision='no'
            )
            return {'data': dummy_data, 'layout': layout},\
                   {'data': dummy_data, 'layout': layout}, 0, 0, 0, 0

        if trigger['prop_id'] == 'core-map.relayoutData' and core_map is not \
                None:
            if 'mapbox.pitch' in core_relayout_data:

                mapbox = dict(
                    accesstoken=access_token,
                    bearing=core_relayout_data['mapbox.bearing'],
                    center=core_relayout_data['mapbox.center'],
                    pitch=core_relayout_data['mapbox.pitch'],
                    zoom=core_relayout_data['mapbox.zoom'],
                    style='light'
                    )

                core_map['layout']['mapbox'] = mapbox
                unc_map['layout']['mapbox'] = mapbox

                return core_map, unc_map, cmax, cmin, unc_cmax, unc_cmin
            else:
                return core_map, unc_map, cmax, cmin, unc_cmax, unc_cmin

        elif trigger['prop_id'] == 'unc-map.relayoutData' and unc_map is not \
                None:
            if 'mapbox.pitch' in unc_relayout_data:

                mapbox = dict(
                    accesstoken=access_token,
                    bearing=unc_relayout_data['mapbox.bearing'],
                    center=unc_relayout_data['mapbox.center'],
                    pitch=unc_relayout_data['mapbox.pitch'],
                    zoom=unc_relayout_data['mapbox.zoom'],
                    style='light'
                    )

                core_map['layout']['mapbox'] = mapbox
                unc_map['layout']['mapbox'] = mapbox

                return core_map, unc_map, cmax, cmin, unc_cmax, unc_cmin
            else:
                return core_map, unc_map, cmax, cmin, unc_cmax, unc_cmin

        if trigger['prop_id'] != 'colorscale_update.n_clicks':
            maxmin = None
        else:
            try:
                maxmin = [float(cmin), float(cmax), float(unc_cmin),
                          float(unc_cmax)]
            except:
                maxmin = []
                for i in range(4):

                    maxmin.append(float(0.0))

        if trigger['prop_id'] == 'time-slider.value' and \
                isinstance(trigger['value'], int) and parameter is not None:
            # updates map if the time slider value is changed when param is
            # selected
            if trigger['value']:
                if trigger['value'] != 0:

                    # Extract timestamp from slider
                    timestamp = trigger['value']
                    if maxmin is not None:
                        maps = app.plotter.update_maps(timestamp, parameter,
                                                       maxmin)
                        cmax = maps[0]['data'][0]['marker'].cmax
                        cmin = maps[0]['data'][0]['marker'].cmin
                        unc_cmax = maps[1]['data'][0]['marker'].cmax
                        unc_cmin = maps[1]['data'][0]['marker'].cmin

                        return maps[0], maps[1], cmax, cmin, unc_cmax, unc_cmin

                    else:
                        maps = app.plotter.update_maps(timestamp, parameter,
                                                       maxmin)
                        cmax = maps[0]['data'][0]['marker'].cmax
                        cmin = maps[0]['data'][0]['marker'].cmin
                        unc_cmax = maps[1]['data'][0]['marker'].cmax
                        unc_cmin = maps[1]['data'][0]['marker'].cmin

                        return maps[0], maps[1], cmax, cmin, unc_cmax, unc_cmin
                else:
                    # Extract timestamp from timeseries plot
                    timestamp = pd.Timestamp(
                        input_slider['value']['points'][0]['x'])
                    maps = app.plotter.update_maps(timestamp, parameter)

                    cmax = maps[0]['data'][0]['marker'].cmax
                    cmin = maps[0]['data'][0]['marker'].cmin
                    unc_cmax = maps[1]['data'][0]['marker'].cmax
                    unc_cmin = maps[1]['data'][0]['marker'].cmin
                    # the code above is used to retrive the maxmimum and
                    # minimum values from the map data for core and
                    # uncertainty maps

                    return maps[0], maps[1], cmax, cmin, unc_cmax, unc_cmin
        elif n_clicks and trigger['prop_id'] == 'select2.n_clicks':
            # updates uncertainty map if so that it displays a different
            # parameter
            if parameter2 is not None and maxmin is None:
                # updates maps if parameter 2 is selected and maxmin is none

                if isinstance(input_slider, int):

                    unc_map = app.plotter.update_unc_map(
                        time_slider, parameter2, maxmin)
                    core_map = app.plotter.update_unc_map(
                        time_slider, parameter, maxmin)
                    maps = core_map, unc_map

                    cmax = maps[0]['data'][0]['marker'].cmax
                    cmin = maps[0]['data'][0]['marker'].cmin
                    unc_cmax = maps[1]['data'][0]['marker'].cmax
                    unc_cmin = maps[1]['data'][0]['marker'].cmin

                    return maps[0], maps[1], cmax, cmin, unc_cmax, unc_cmin
                else:
                    # Extract timestamp from timeseries plot

                    timestamp = pd.Timestamp(
                        input_slider['value']['points'][0]['x'])
                    maps = app.plotter.update_maps(timestamp, parameter,
                                                   maxmin)
                    cmax = maps[0]['data'][0]['marker'].cmax
                    cmin = maps[0]['data'][0]['marker'].cmin
                    unc_cmax = maps[1]['data'][0]['marker'].cmax
                    unc_cmin = maps[1]['data'][0]['marker'].cmin

                    return maps[0], maps[1], cmax, cmin, unc_cmax, unc_cmin
            elif parameter2 is not None and maxmin is not None:

                unc_maxmin = [float(unc_cmin), float(unc_cmax), 0, 0]
                unc_map = app.plotter.update_unc_map(
                    time_slider, parameter2, unc_maxmin)
                core_map = app.plotter.update_unc_map(
                    time_slider, parameter, maxmin)
                maps = core_map, unc_map

                cmax = maps[0]['data'][0]['marker'].cmax
                cmin = maps[0]['data'][0]['marker'].cmin
                unc_cmax = maps[1]['data'][0]['marker'].cmax
                unc_cmin = maps[1]['data'][0]['marker'].cmin

                return maps[0], maps[1], cmax, cmin, unc_cmax, unc_cmin
            else:
                maps = app.plotter.update_maps(time_slider, parameter,
                                               maxmin)
                cmax = maps[0]['data'][0]['marker'].cmax
                cmin = maps[0]['data'][0]['marker'].cmin
                unc_cmax = maps[1]['data'][0]['marker'].cmax
                unc_cmin = maps[1]['data'][0]['marker'].cmin

                return maps[0], maps[1], cmax, cmin, unc_cmax, unc_cmin

        elif n_clicks2 and trigger['prop_id'] == 'colorscale_update.n_clicks':
            if parameter2 is None:

                maps = app.plotter.update_maps(time_slider, parameter,
                                               maxmin)
                cmax = maps[0]['data'][0]['marker'].cmax
                cmin = maps[0]['data'][0]['marker'].cmin
                unc_cmax = maps[1]['data'][0]['marker'].cmax
                unc_cmin = maps[1]['data'][0]['marker'].cmin

                return maps[0], maps[1], cmax, cmin, unc_cmax, unc_cmin

            elif parameter2 is not None and maxmin is not None:

                unc_maxmin = [float(unc_cmin), float(unc_cmax), 0, 0]
                unc_map = app.plotter.update_unc_map(
                    time_slider, parameter2, unc_maxmin)
                core_map = app.plotter.update_unc_map(
                    time_slider, parameter, maxmin)

                maps = core_map, unc_map
                cmax = maps[0]['data'][0]['marker'].cmax
                cmin = maps[0]['data'][0]['marker'].cmin
                unc_cmax = maps[1]['data'][0]['marker'].cmax
                unc_cmin = maps[1]['data'][0]['marker'].cmin

                return maps[0], maps[1], cmax, cmin, unc_cmax, unc_cmin
            else:

                maps = app.plotter.update_maps(time_slider, parameter,
                                               maxmin)
                cmax = maps[0]['data'][0]['marker'].cmax
                cmin = maps[0]['data'][0]['marker'].cmin
                unc_cmax = maps[1]['data'][0]['marker'].cmax
                unc_cmin = maps[1]['data'][0]['marker'].cmin

                return maps[0], maps[1], cmax, cmin, unc_cmax, unc_cmin

        else:
            pass

    @staticmethod
    @app.callback(
        [Output('dropdown_container2', 'style'),
         Output('select2', 'style'),
         Output('parameter_select2', 'disabled')],
        [Input('visibility_button', 'n_clicks')],
        [State('dropdown_container2', 'style'),
         State('select2', 'style')])
    def visibility_function(n_clicks, dropdown_state, select_state):
        """
        updates page so that second dropdown for the second graphs is visible
        in order to show 2nd parameter in 2nd graph
        :param n_clicks:
        :param dropdown_state:
        :param select_state:
        :return:
        """
        if n_clicks:
            vis = dropdown_state['visibility']
            if vis == 'none' or vis == 'hidden':

                dropdown_state['visibility'] = 'visible'

                select_state['visibility'] = 'visible'

                return dropdown_state, select_state, False

            elif vis == 'visible' or vis == 'visible':

                dropdown_state['visibility'] = 'hidden'

                select_state['visibility'] = 'hidden'
                return dropdown_state, select_state, True

        else:
            return dropdown_state, select_state, True

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
            timestamp = pd.Timestamp(dt.datetime.strptime(
                trigger['value']['points'][0]['x'], "%d-%m-%Y"))

            return timestamp.value
        else:
            pass

    @staticmethod
    @app.callback(
        Output('markdown', 'children'),
        [Input('time-slider', 'value')])
    def update_markup(selected_time):
        """
        Post the date of the marker to the markdown string to make sure we're
        seeing time updating
        :param selected_time:
        :return:
        """

        trigger = dash.callback_context.triggered[0]

        if trigger['value']:

            date = pd.Timestamp(selected_time).to_pydatetime().strftime(
                "%d-%m-%Y")

            return f"Date: {date}"

        else:

            pass


if __name__ == "__main__":

    # MultiplyVis()

    MultiplyVis(os.path.abspath('../data_2/kafkaout_Barrax_Q1_noprior_S2/'))
