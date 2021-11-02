import dash
from dash import html, dcc
from textwrap import dedent as d

import numpy as np, pandas as pd
from pandas.io.formats import style

from dataWorkersLikeMe import * # Import the data and visualisation code
default_code = '2621'


tabSearch= dcc.Tab(label='Search', value='Search', style={'text-align':'center', 'display':'block'}, children=[
   html.Div([
    html.Div(dcc.Markdown('''Search for an occupation''')),
    html.Div(className='row',
       children=[dcc.Dropdown(id="occupationChoiceDropdown", options=[{'label':nameMap[occ], 'value': occ} for occ in totalOcc4Digit.keys() if occ in nameMap], value=default_code),
        html.Button('Investigate', id='goToWorkerButton', n_clicks=0)
       ]),
   ], className='row', style={'text-align':'center', 'position':'fixed', 'left':'25%', 'bottom':'50%', 'width':'50%'}),
])

tabWorkersLikeMe = dcc.Tab(label='Workers Like Me', value='WorkersLikeMe', style = {'display':'block'}, children=[
    dcc.Store(id='occupationChoice', storage_type='local', data={'occupation':default_code}),
    html.Div(className="row", children=dcc.Markdown(d("""This tool which is very much a work in progress will take your occupation as input and tell you where other works like you are currently working and living. If you're thinking of changing jobs or are curious about what jobs would suit your skills take the [JobOutlook Skills Match](https://joboutlook.gov.au/career-tools/skills-match/#/). If you're thinking about what careers might suit you take the [JobOutlook Career Quiz](https://joboutlook.gov.au/career-tools/career-quiz/#/)."""))),
    html.Div(className="row", children=[
        html.Div(className="six columns", 
        children=dcc.Graph(id="worker-map-PUR",
            figure=jobsMap.plot_jobs_on_map(default_code, 'PUR'))),
        html.Div(className="six columns", 
        children=dcc.Graph(id="worker-map-POW",
            figure=jobsMap.plot_jobs_on_map(default_code, 'POW'))),
        ]),
     html.Div(className="row", id="worker-all-plot")
    ]
)

# Define an empty plotly figure
empty_figure = {}
