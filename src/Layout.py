import dash_html_components as html
import dash_core_components as dcc

class Layout:

    @staticmethod
    def index(plotter):

        page = html.Div([

             # first logo:

             html.Div(id='header_container', className =
                 'middle_container', children=[

                 html.Div(id='topleft_logo', children=[
                     html.A([html.Img(src='assets/logo.png')],
                            href='http://www.multiply-h2020.eu/')
                 ]),

                 html.Div(id='main_title_container', children=[
                     html.H1('MULTIPLY Visualisations',
                            id='main_title')
                 ]),

                 html.Div(style={'clear': 'left'})

                 # html.Div(id='descriptor_container',children=[
                 #     html.P('Some filler text',
                 #            id='descriptor')
                 # ])

                ])
             ,

             html.Div(id='data_background', children=[

                 # html.Div(id='subtitle_container',children=[
                 #    html.P('Data Display:', id='subtitle')
                 #    ])
                 #    ,

                 html.Div(className='middle_container', children=[
                     html.Div(id='select_box',children=[

                         html.Div(id='dropdown_container', children=[
                             dcc.Markdown(
                                 id='select_text',
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
                     # html.Div(id='unc_expl_container', children=[
                     #     html.P('Some description.', id='unc_expl')
                     # ])

                 ])
                 ,
                 html.Div(style={'clear': 'left'})

                    ,


                 html.Div(className='middle_container', children=[

                    html.Div(id='core_vis_container',
                             className='map_container', children=[

                        html.H2('Derived data', id='core_data_title'),

                        html.Div(id='data_container',children=[
                            dcc.Graph(id='core-map')
                            ]),
                    ])
                    ,
                    html.Div(id='unc_vis_container', className='map_container',
                             children=[

                        html.H2('Uncertainty', id='unc_data_title'),

                        html.Div(id='unc_container', children=[
                            dcc.Graph(id='unc-map')
                            ]),


                    ]),
                    html.Div(style={'clear': 'left'})
                    ]),

                 html.P(id="helptext", className='middle_container',
                        children='The Uncertainty map displays negative '
                        'uncertainty only. The timeseries plot '
                        'below displays both positive and negative '
                        'values. Where the uncertainty is infinity, this is '
                        'represented on the timeseries as the value zero.'),

                 html.Div(id="slider_time_container", className='middle_container',
                          children=[
                    html.Div(id='slider_container', children=[
                        dcc.Slider(id='time-slider')
                    ]),

                    html.Div(dcc.Markdown(id='markdown', children="")),
                  ]),

                 html.Div(id="times_container", className='middle_container',
                          children=[
                     html.Div(id='timeseries_container',children=
                        [dcc.Graph(id='pixel_timeseries')

                        ]),
                     html.Button(
                         id='download_button',
                         n_clicks=0,
                         children=[html.A(
                             'Download Data',
                             id='download_link',
                             download="rawdata.csv",
                             href="",
                             target="_blank")
                         ])
                ])


             ])
                 ,
             html.Div(id='partners_container', children=[
                html.Div(id='p1_container', className="logo_container", children=[
                    html.A([html.Img(id='p1', src='assets/l1.png')
                    ], href='https://ec.europa.eu/')]),

                html.Div(id='p2_container', className="logo_container",
                         children=[
                    html.A([html.Img(id='p2', src='assets/l2.png')],
                           href='http://www.assimila.eu/')
                    ,
                    html.P('© 2019 Assimila Ltd',id='copyright')
                    ]),

                html.Div(id='p3_container', className="logo_container",
                         children=[
                    html.A([html.Img(id='p3',src='assets/l3.png')],
                           href='http://www.multiply-h2020.eu/')
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

    @staticmethod
    def external_stylesheets():
        """
        Extrnal stylesheets to be used
        :return:
        """
        # stylesheets = [
        #     "https://fonts.googleapis.com/css?family=Open+Sans&display=swap",
        # ]

        stylesheets ="https://fonts.googleapis.com/css?family=Open+Sans&display=swap"

        return stylesheets