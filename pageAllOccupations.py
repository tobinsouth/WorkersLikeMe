import dash
from dash import html, dcc
from textwrap import dedent as d

import numpy as np, pandas as pd

from dataAllOccupations import *

tabAllOccupations = dcc.Tab(label='All Occupations', value = 'AllOccupations', style = {'display':'block'}, children=[
    html.Div(
        className="row",
        style = {'text-align':'center', 'margin-top':'20px'},
        children=[ dcc.Markdown(d("""
        ## Every Job Category in South Australia
        We can view all of the jobs in south australia as a network where each job is connected to other jobs that have similar skills.
        Click on the circles in this network to see information about the job.
        You can change how the size and colour of the nodes are displayed by clicking on the dropdown menu.
       """))
        ]
    ),
    html.Div(className="row", children=html.Div(
                className="twelve columns",
                children=[dcc.Graph(id="labour-graph",
                                    figure=labourNetwork.main_figure)],
            )),
    html.Div(
        className="row",
        children=[
            html.Div(
                className="six columns",
                children=html.Div(id='occupation-information-AllOcc',
                    children="Click on a node to see more information"),
            ),
            html.Div(
                className="six columns",
                children=[
                     html.Div(className="row", children=[
                         html.Div(
                        className="six columns",
                        children=[
                            dcc.Markdown(d("""
                            #### Color Choice
                            """)),
                            dcc.Dropdown(id="color_choice", value="Gender Share Numeric", options=[{'label':key.replace('Numeric', ''), 'value': key} for key in variable_descriptions.keys()]),
                            html.Div(id="color_choice_output")
                        ],),
                        html.Div(
                            className="six columns",
                            children=[
                                dcc.Markdown(d("""
                                \n
                                #### Size Choice
                                """)),
                                dcc.Dropdown(id="size_choice", value="Total SA Workers", options=[{'label':key.replace('Numeric', ''), 'value': key} for key in variable_descriptions.keys()]),
                                html.Div(id="size_choice_output")
                            ]),
                    ]),
                    html.Div(
                        className="twelve columns",
                        children=[dcc.Graph(id="labour-scatter",
                                    figure=
                                    labourNetwork.scatterplot("Total SA Workers", 'Gender Share Numeric'))],
                     ),
                ]
            ),
        ]
    )
])
