import dash_html_components as html
import dash_core_components as dcc

class Layout:

    @staticmethod
    def index(plotter):

        page = html.Div([

             # first logo:

             html.Div(children=[

                 html.Div(id='topleft_logo', children=[
                     html.Img(src='assets/logo.png'),
                 ]),

                 html.Div(id='main_title_container', children=[
                     html.P('MULTIPLY Visualisations',
                            id='main_title')
                 ]),

                 html.Div(id='descriptor_container',children=[
                     html.P('Some filler text',
                            id='descriptor')
                 ])

                ])
             ,

             html.Div(id='data_background', children=[

                 html.Div(id='subtitle_container',children=[
                    html.P('Data Display:', id='subtitle')
                    ])
                    ,
                 html.Div(id='unc_expl_container', children=[
                    html.P('Some description.', id='unc_expl')
                    ])
                    ,
                 html.Div(style={'clear': 'left'})

                    ,

                 html.Div(children=[

                     html.Div(id='dropdown_container', children=[
                         dcc.Markdown(
                             id='markdown',
                             children="Select Parameter:"),
                         plotter.generate_parameter_dropdown()
                     ]),
                     html.Div(id='button_container', children=[
                         html.Button(
                             id='select',
                             n_clicks=0,
                             children='Select')
                     ])
                 ])
                 ,

                 html.Div(children=[

                    html.Div(id='data_container',children=[
                        dcc.Graph(id='core-map')
                        ])
                     ,
                    html.Div(id='unc_container', children=[
                        dcc.Graph(id='unc-map')
                        ])

                    ])
                    ,



                 html.Div(id='slider_container', children=[
                    dcc.Slider(id='time-slider')
                    ]),

                 html.Div(id='timeseries_container',children=
                    [dcc.Graph(id='pixel_timeseries')

                    ])

                 ])


                #      html.Div(
                #          [dcc.Markdown(
                #              id='markdown',
                #              children="default text")]),
                #      plotter.generate_parameter_dropdown(),
                #      html.Button(
                #          id='select',
                #          n_clicks=0,
                #          children='Select'),
                #      html.Div(
                #          id='slider-container',
                #          style={
                #              'width': '80%',
                #              'display':'inline-block',
                #              'margin-bottom':'40px',
                #              'height':'40px'},
                #          children=[dcc.Slider(id='time-slider')]),
                #      html.Div(
                #          style={
                #              'width': '40%',
                #              'float':'left',
                #              'display':'inline-block'},
                #          children=[dcc.Graph(id='core-map')]),
                #      html.Div(
                #          style={
                #              'width': '40%',
                #              'float':'left',
                #              'display':'inline-block'},
                #          children=[dcc.Graph(id='unc-map'),]),
                #      html.Div(
                #          style={
                #              'width': '80%',
                #              'float':'left',
                #              'display':'inline-block'},
                #          children=dcc.Graph(id='pixel_timeseries'))
                 ])

        return page