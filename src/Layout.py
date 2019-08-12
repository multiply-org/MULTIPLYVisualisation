import dash_html_components as html
import dash_core_components as dcc


class Layout:

    @staticmethod
    def index(plotter):

        page = html.Div([

             # first logo:

             html.Div(id='header_container', className='middle_container',
                      children=[
                                html.Div(id='partners_container', children=[
                                    html.Div(id='p1_container',
                                             className="logo_container",
                                             children=[html.A(
                                                 [html.Img(
                                                     id='p1',
                                                     src='assets/l1.png')],
                                                 href='https://ec.europa.eu/')
                                             ]),

                                    html.Div(id='p2_container',
                                             className="logo_container",
                                             children=[
                                                 html.A([html.Img(
                                                     id='p2',
                                                     src='assets/l2.png')],
                                                     href='http://www.assimila'
                                                          '.eu/'),

                                                 html.P('© 2019 Assimila Ltd',
                                                        id='copyright')
                                             ]),

                                    html.Div(id='p3_container',
                                             className="logo_container",
                                             children=[html.A([
                                                 html.Img(
                                                     id='p3',
                                                     src='assets/l3.png')],
                                                 href='http://www.multiply-'
                                                      'h2020.eu/')],
                                             ),
                                    html.Div(id='main_title_container',
                                             children=[
                                                 html.H1(
                                                     'MULTIPLY Visualisations',
                                                     id='main_title')])
                                ])
                      ]),

             html.Div(id='data_background', children=[

                 # html.Div(id='subtitle_container',children=[
                 #    html.P('Data Display:', id='subtitle')
                 #    ])
                 #    ,
                 html.Div(className='side_container',
                          id='sidebar',
                          children=[
                              html.Div(id='dropdown_container', children=[
                                  dcc.Markdown(
                                      id='select_text1',
                                      children="Select Parameter:"),
                                  plotter.generate_parameter_dropdown(
                                      "parameter_select"),
                                    html.Button(
                                          id='select',
                                          n_clicks=0,
                                          children='Select',
                                          style={'display': 'block'
                                                 }),
                                    html.Button(
                                        id='colorscale_update',
                                        n_clicks=0,
                                        children='Refresh colorscale',
                                        style={'display': 'block'
                                               }),
                                    html.Button(
                                          id='visibility_button',
                                          n_clicks=0,
                                          style={
                                              'display': 'block'
                                          },
                                          children='Toggle Second parameter')
                                      ]),

                              html.Div(id='dropdown_container2', children=[
                                  dcc.Markdown(
                                      id='select_text2',
                                      children="Select Parameter:"
                                  ),
                                  plotter.generate_parameter_dropdown(
                                      "parameter_select2"),
                                  html.Button(
                                      id='select2',
                                      n_clicks=0,
                                      children='Select',
                                      style={
                                          'display': 'block',
                                          'visibility': 'hidden'})
                              ], style={
                                  'display': 'block',
                                  'visibility': 'hidden'}),
                              html.Div(id='help_container', className='sidebar',
                                       children=[
                                        html.P('The Uncertainty map displays '
                                               'negative uncertainty only. The '
                                               'timeseries plot below displays '
                                               'both positive and negative '
                                               'values. ''Where the uncertainty'
                                               ' is infinity, this is '
                                               'represented on the timeseries'
                                               ' as the value zero.'
                                               'If you input 0 to the '
                                               'colourscale inputs it will '
                                               'reset them to their original '
                                               'value.'),
                                       ]),
                              html.Button(
                                  id='download_button',
                                  style={},
                                  n_clicks=0,
                                  children=[html.A(
                                      'Download Data',
                                      id='download_link',
                                      download="rawdata.csv",
                                      href="",
                                      target="_blank")
                                  ])
                          ],
                          style={'max-width': '12%',
                                 'display': 'inline-block',
                                 'float': 'left'}),

                 html.Div(id='main-div',className='middle_container', children=[

                    html.Div(id='core_vis_container', className='map_container',
                             children=[
                                 dcc.Input(id='cmax',
                                           className='input_box',
                                           type='text',
                                           value=0.0,
                                           style={'display': '',
                                                  'margin-top': '6.5%'}),

                                 html.H2('Derived data', id='core_data_title'),

                                 html.Div(id='data_container', children=[
                                     dcc.Graph(id='core-map',
                                               config={'modeBarButtonsToRemove'
                                                        :['lasso2d']}),
                                     dcc.Input(id='cmin',
                                               className='input_box',
                                               value=0.0,
                                               style={'display': ''})
                                 ]),
                             ]),

                    html.Div(id='unc_vis_container', className='map_container',
                             children=[
                                 dcc.Input(id='unc_cmax',
                                           className='input_box',
                                           type='text',
                                           value=0.0,
                                           style={'display': '',
                                                  'margin-top': '6.5%'}),
                                 html.H2('Uncertainty', id='unc_data_title'),
                                 html.Div(id='unc_container', children=[
                                     dcc.Graph(id='unc-map',
                                               config={'modeBarButtonsToRemove'
                                                       :['lasso2d']}
                                               ),
                                     dcc.Input(id='unc_cmin',
                                               className='input_box',
                                               type='text',
                                               value=0.0,
                                               style={'display': ''})
                                 ]),
                             ]),
                    html.Div(style={'clear': 'left'})
                    ],
                          style={'display': 'block'}),

                 html.Div(id="slider_time_container",
                          className='middle_container',
                          children=[
                              html.Div(id='slider_container', children=[
                                  dcc.Slider(id='time-slider')
                              ]),
                              html.Div(dcc.Markdown(id='markdown', children="")
                                       ),
                          ]),

                 html.Div(id="times_container", className='middle_container',
                          children=[html.Div(id='timeseries_container',
                                             children=[dcc.Graph(
                                                 id='pixel_timeseries')])])
             ])
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