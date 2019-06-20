import dash_html_components as html
import dash_core_components as dcc

class Layout:

    @staticmethod
    def index(plotter):

        page = html.Div([
                        html.H1(
                            children='Multiply Visulisation',
                            style={'textAlign': 'center'}),
                        html.Div(
                            [dcc.Markdown(
                                id='markdown',
                                children="Select a datatype")]),
                        plotter.generate_parameter_dropdown(),
                        html.Button(
                            id='select',
                            n_clicks=0,
                            children='Select'),
                        html.Div(
                            id='slider-container',
                            style={
                                'width': '80%',
                                'display':'inline-block',
                                'margin-bottom':'40px',
                                'height':'40px'},
                            children=[dcc.Slider(id='time-slider')]),
                        html.Div(
                            style={
                                'width': '40%',
                                'float':'left',
                                'display':'inline-block'},
                            children=[dcc.Graph(id='core-map')]),
                        html.Div(
                            style={
                                'width': '40%',
                                'float':'left',
                                'display':'inline-block'},
                            children=[dcc.Graph(id='unc-map'),]),
                        html.Div(
                            style={
                                'width': '80%',
                                'float':'left',
                                'display':'inline-block'},
                            children=dcc.Graph(id='pixel_timeseries')),
                        html.A(
                            'Download Data',
                            id='download-link',
                            download="rawdata.csv",
                            href="",
                            target="_blank"
                        )
                    ])

        return page