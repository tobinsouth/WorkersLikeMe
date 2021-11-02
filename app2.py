#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dash
from textwrap import dedent as d
from dash import Input, Output, State, html, dcc, callback_context

from pageAllOccupations import *
from pageWorkersLikeMe import *


# import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_scripts = ['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)
app.title = "South Australian Job Market"


app.layout = html.Div(children=[
    html.Div(
        className="row",  style={'horizontalAlign': 'middle'},
        children=[ dcc.Markdown(d("""
        # Workers Like Me
       """), style={'text-align': 'center'})
        ]
    ),
    dcc.Tabs(id="tabs", 
        # style={'display':'block'}, 
        children=[tabSearch, tabWorkersLikeMe, tabAllOccupations], value = 'Search'),
    html.Div(
        className="row", style={'text-align': 'center', 'position':'fixed', 'bottom':'10%', 'background-color': 'white'},
        children=html.Button('Explore All Occupations', id='AllOccupationsButton', 
        style = {'width':'50%', 'position':'fixed', 'bottom':'5%', 'left': '25%'}
        ),
    )
])










# Update workers like me tab
@app.callback(Output('worker-map-PUR', 'figure'), Input('occupationChoiceDropdown','value'))
def update_worker_map_PUR(occupationChoice):
    if occupationChoice:
        return jobsMap.plot_jobs_on_map(occupationChoice, 'PUR')
    else:
        return empty_figure
@app.callback(Output('worker-map-POW', 'figure'), Input('occupationChoiceDropdown','value'))
def update_worker_map_POW(occupationChoice):
    print('update_worker_map_POW', occupationChoice)
    if occupationChoice:
        return jobsMap.plot_jobs_on_map(occupationChoice, 'POW')
    else:
        return empty_figure

@app.callback(Output('worker-all-plot', 'children'), Input('occupationChoiceDropdown','value'))
def update_worker_all_plot(occupationChoice):
    if occupationChoice:
        return make_all_data_tables(occupationChoice)
    else:
        return None


# Update All Occupations Tab

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
    Output('occupation-information-AllOcc', 'children'), Input('labour-graph', 'clickData'))
def update_occupation_information_AllOcc(clickData):
    if clickData is None:
        return 'Click on a node to see more information'
    else:
        return '{}'.format(clickData)



# Update workers choice
@app.callback(Output('occupationChoice', 'data'), Input('goToWorkerButton', 'n_clicks'), State('occupationChoiceDropdown','value'))
def update_occupationChoice(goToWorkerButton, occupationChoiceDropdown):
    if occupationChoiceDropdown:
        print('update_occupationChoice', occupationChoiceDropdown)
        return {'occupation':occupationChoiceDropdown} 
    else:
        raise dash.exceptions.PreventUpdate

# Switch layouts    
@app.callback(Output('tabs', 'value'),Input('AllOccupationsButton', 'n_clicks'), Input('goToWorkerButton', 'n_clicks'))
def switch_tab(AllOccupationsButton, goToWorkerButton):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    print('switch_tab', changed_id)
    if 'AllOccupationsButton' in changed_id:
        return 'AllOccupations'
    elif 'goToWorkerButton' in changed_id:
        return 'WorkersLikeMe'
    else:
        raise dash.exceptions.PreventUpdate
if __name__ == '__main__':
    app.run_server(debug=True)
