#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from textwrap import dedent as d
from dash_html_components.Figure import Figure

from igraph import Graph


from skillsFunctions import *
from textDescriptions import *


# import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_scripts = ['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)
app.title = "South Australian Job Market"

# Setup the website layout.
app.layout = html.Div(dcc.Tabs(
    [dcc.Tab(label='Labour Networks', children = [
    html.Div(
        className="row",
        children=[ dcc.Markdown(d("""
        ## Labour Market Skills in South Australia
       """))
        ]
    ),
    html.Div(
        className="row",
        children=[
            ##############################################left side two input components
            html.Div(
                className="five columns",
                children=[
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.Markdown(d("""
                            #### Color Choice
                            """)),
                            dcc.Dropdown(id="color_choice", value="Total SA Workers", options=[{'label':key.replace('Numeric', ''), 'value': key} for key in variable_descriptions.keys()]),
                            html.Div(id="color_choice_output")
                        ],
                        # style={'height': '300px'}
                    ),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.Markdown(d("""
                            \n
                            #### Size Choice
                            """)),
                            dcc.Dropdown(id="size_choice", value="None", options=[{'label':key.replace('Numeric', ''), 'value': key} for key in variable_descriptions.keys()]),
                            html.Div(id="size_choice_output")
                        ],
                        # style={'height': '300px'}
                    ),
                     html.Div(
                        className="twelve columns",
                        children=[dcc.Graph(id="labour-scatter",
                                    figure=
                                    labourNetwork.scatterplot("Total SA Workers", 'Gender Share Numeric'))],
                     )
                ]
            ),
            html.Div(
                className="seven columns",
                children=[dcc.Graph(id="labour-graph",
                                    figure=labourNetwork.main_figure)],
            ),
        ]
    )
    # html.Div(style={'height': '50px'}),
    # html.Div(
    #     className="row",
    #     children=[ 
    #         html.Div(
    #             className="six columns",
    #             children=[
    #                 dcc.Markdown(d(
    #                     """
    #                     ## Detailed Resilience Estimation
    # html.Div(
    #     className="row",
    #     children=[
    #          html.Div(
    #             className="six columns",
    #             children=[
    #                 dcc.Markdown(d(
    #                     """
    #                     ## Detailed Resilience Estimation

    #                     Labour markets are like an ecosystem. 
    #                     Strong interconnections between diverse occupations lead to economies that are more resilient to shocks.
    #                     COVID-19 presented a major shock to economies around the world, 
    #                     and we've been working to understand how the diversity of our labour markets has effected our states resilience.  


    #                     In particular we can define the embeddedness, $e\_j^r$, of a job, $j$, in a region, 
    #                     $r$ by the number and strength of connections to other jobs in a labour network like above.
    #                     We regions labour market will look different, an each has an overall resilience value, $e\_{total}^r$, 
    #                     which can define how interconnected the regions market is, 
    #                     $e\_{total}^r = \sum\_j (e\_j^r)^2 / \sum\_{a,b \in \text{jobs}} A\_{a,b}$, for a network adjacency matrix $A$.


    #                     These market insights, combined with a Bayesian approach to unemployment data,
    #                     can help us understand the detailed risks faced by economies in the many regions of Australia.

    #                     """
    #                 )),
    #                 html.Div([
    #                     html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(
    #                         open('assets/April Total Employment Losses.png', 'rb').read()).decode()), style={'width': '100%'})
    #                 ])
    #             ]
    #         ),
    #     ]
    # )
]),
dcc.Tab(label='Workers Like Me', children = [
    html.Div(className="row", children=dcc.Markdown(d("""This tool which is very much a work in progress will take your occupation as input and tell you where other works like you are currently working and living. If you're thinking of changing jobs or are curious about what jobs would suit your skills take the [JobOutlook Skills Match](https://joboutlook.gov.au/career-tools/skills-match/#/). If you're thinking about what careers might suit you take the [JobOutlook Career Quiz](https://joboutlook.gov.au/career-tools/career-quiz/#/)."""))),
    html.Div(className="row", children=[
        html.Div(className="four columns", children=[
            dcc.Markdown(d("""
            #### What is your occupation?
            Find your occupation and we will shop you where people in the same occupation are working and living.
            """))
        ]),
        html.Div(className="four columns", children=[
            dcc.Dropdown(id="occupation_choice", value="Sales Assistants (General)", options=[{'label':title, 'value': title} for title, code in jobs_to_codes.items()]),
            # html.Div(id="occupation_choice_output")
        ]),
        html.Div(className="four columns", children=[
           dcc.RadioItems(
                id="POWorPURradio",
                options=[
                    {'label': 'Place of Usual Residence', 'value': 'PUR'},
                    {'label': 'Place of Work', 'value': 'POW'},
                ],
                value='PUR')
        ]),
    ]),
    html.Div(className="row", 
    children=dcc.Graph(id="worker-map",
        figure=jobsMap.plot_jobs_on_map('Sales Assistants (General)', 'PUR'))),
    ]
)]
))


# This line is needed for webhosting
server = app.server 

######################################################################################################################################################################
# These callbacks are what will make everything interactive
######################################################################################################################################################################

# Labour Networks Tab Callbacks
@app.callback(
    dash.dependencies.Output('labour-graph', 'figure'),
    [dash.dependencies.Input('color_choice', 'value'), 
     dash.dependencies.Input('size_choice', 'value')])
def update_main_labour_output(color_choice, size_choice):
    return labourNetwork.get_updated_graph(color_choice, size_choice)

@app.callback(
    dash.dependencies.Output('labour-scatter', 'figure'),
    [dash.dependencies.Input('color_choice', 'value'), 
     dash.dependencies.Input('size_choice', 'value')])
def update_main_labour_output(color_choice, size_choice):
    return labourNetwork.scatterplot(color_choice, size_choice)


@app.callback(
    dash.dependencies.Output('color_choice_output', 'children'),
    [dash.dependencies.Input('color_choice', 'value')])
def update_color_choice_output(color_choice):
    return variable_descriptions[color_choice]

@app.callback(
    dash.dependencies.Output('size_choice_output', 'children'),
    [dash.dependencies.Input('size_choice', 'value')])
def update_size_choice_output(size_choice):
    return variable_descriptions[size_choice]


# Worker map tab

@app.callback(
    dash.dependencies.Output('worker-map', 'figure'),
    [dash.dependencies.Input('occupation_choice', 'value'), 
     dash.dependencies.Input('POWorPURradio', 'value')])
def update_main_labour_output(occupation_choice, POWorPURradio):
    return jobsMap.plot_jobs_on_map(occupation_choice, POWorPURradio)





if __name__ == '__main__':
    app.run_server()

