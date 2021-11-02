import igraph as ig, numpy as np, pandas as pd

import plotly
import dash_core_components as dcc
import dash_html_components as html
from textwrap import dedent as d
import plotly.graph_objs as go
# import base64 # For rendering images


import geopandas as gpd
import plotly.express as px


# IMPORTANT: Load in two key datasets
# 1. The network of occupations linked by skills with metadata
skill_scape_graph = ig.Graph.Read_GraphML("data/skill_scape_graph.graphml")

# 2. Load in the matrix of person counts by occupation in each SA2 where they leave (place of usual residence) in the 2016 census 
occ4DigitvsSA2PUR2016 = pd.read_csv('data/Occ4DigitvsSA2PUR2016.csv')
occ4DigitvsSA2PUR2016.set_index('SA2', inplace=True)
totalOcc4Digit = occ4DigitvsSA2PUR2016.sum(axis=0).to_dict() # Sum over all areas

# Information parameters
informationParameters = ['title','Weekly Pay', 'Future Growth', 'Employment Size', 'Skill level rating', 'Full-Time Share', 'Average full-time', 'Average age', 'Gender Share',]

# Visualise-able parameters
visualParameters = ['Employment Size Numeric', 'Skill level rating', 'Full-Time Share Numeric', 'Average full-time Numeric', 'Average age Numeric', 'Gender Share Numeric', 'Weekly Pay Numeric'] # + 'Future Growth' but is categorial


class LabourNetwork():
    """
    This class exists for the purpose of editing the graph and creating the network visualisation. At lot of this is plotly cruft, and I will try to make the important parts clear.
    """
    def __init__(self):
        
        self.four_digit_G = skill_scape_graph

        self.four_digit_G.vs['Total SA Workers'] = [totalOcc4Digit.get(str(int(occ)), 0) for occ in self.four_digit_G.vs['name']]


        self.current_color_choice = "Total SA Workers"
        self.current_size_choice = 'None'

        self.edge_data = self.setup_edges(self.four_digit_G)
        self.edge_weights = np.array(self.four_digit_G.es['weight'])
        self.edge_weights = np.argsort(self.edge_weights) / len(self.edge_weights)

        self.current_threshold = 0
        self.main_figure = self.get_labour_figure()
        self.edge_trace = self.update_threshold(0.2)


    def setup_edges(self, G):
        edge_data = []
        for e in G.es:
            n0, n1 = e.tuple
            x0, y0 = G.vs[n0]['x'], G.vs[n0]['y']
            x1, y1 = G.vs[n1]['x'], G.vs[n1]['y']
            edge_data += [(x0, x1, None, y0, y1, None)]
        return np.array(edge_data)

    def update_threshold(self, threshold):
        if self.current_threshold != threshold:
            ed = self.edge_data[self.edge_weights > threshold,:]
            self.edge_trace = go.Scatter(x=list(ed[:,:3].flatten()), 
                        y=list(ed[:,3:].flatten()),
                        mode='lines',\
                        line={'width': 0.2},\
                        line_shape='spline',\
                        opacity=0.5,\
                        hoverinfo='none')
            self.current_threshold = threshold
            self.main_figure['data'][0] = self.edge_trace

    def update_colors(self, color_choice):
        if self.current_color_choice != color_choice:
            self.main_figure['data'][1]['marker'] = {'size':10, 'color':self.four_digit_G.vs[color_choice], 'cauto':True, 'colorscale':'RdBu', 'colorbar':{'thickness':20, 'title':color_choice}}
            self.current_color_choice = color_choice
            self.update_size(self.current_size_choice)

    def update_size(self, size_choice):
        if size_choice == 'None':
            self.main_figure['data'][1]['marker']['size'] = 0
        else:
            sizes = np.log(np.array(self.four_digit_G.vs[size_choice])+1)
            sizes = list(30*sizes / np.max(sizes))
            self.main_figure['data'][1]['marker']['size'] = sizes
        self.current_size_choice = size_choice


    def get_updated_graph(self, color_choice, size_choice):
        self.update_colors(color_choice)
        self.update_size(size_choice)
        return self.main_figure


    def get_labour_figure(self, colour_by = "Total SA Workers", new_layout = False, edge_trace = None, size = 10):
        """This one does the hard work of actually creating the figure."""
        G = self.four_digit_G

        self.edge_trace = go.Scatter(x=list(self.edge_data[:,:3].flatten()), 
                        y=list(self.edge_data[:,3:].flatten()),
                        mode='lines',\
                        line={'width': 0.2},\
                        line_shape='spline',\
                        opacity=0.5,\
                        hoverinfo='none')

        if new_layout:
            layout = np.array(G.layout_fruchterman_reingold(weights=field).coords)
            G.vs["x"] = [f.item() for f in layout[:,0]]
            G.vs["y"] = [f.item() for f in layout[:,1]]

        node_x = G.vs['x']
        node_y = G.vs['y']
        node_hovertext = [("</br>"+": %s </br>".join(informationParameters)+": %s") % items for items in zip(*[G.vs[iP] for iP in informationParameters])]  

        # color = [plotly.colors.diverging.Portland[c] for c in G.vs[colour_by]]
        if type(size) == int:
            sizes = size
        else:
            sizes =  G.vs[size]
            sizes = np.log(np.array(sizes)+1)
            sizes = list(20*sizes / np.max(sizes))

        node_trace = go.Scatter(x=node_x, y=node_y, hovertext=node_hovertext, text=[], mode='markers+text', textposition="bottom center", \
                                hoverinfo="text", marker={'size': sizes, 'color':self.four_digit_G.vs["Total SA Workers"], 'cauto':True, 'colorscale':'Aggrnyl', 
                                       'colorbar':{'thickness':20, 'title':'Total South<br>Australians<br>Employed'}}, showlegend=True)

        figure = {
                "data": [self.edge_trace, node_trace] ,
                "layout": go.Layout(title='Labour Network Visualization', showlegend=False, hovermode='closest',
                                    margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                                    xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                                    yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                                    height=600,
                                    clickmode='event+select',
                                    )}
        return figure


    def scatterplot(self, x, y):
        """Extra little scatter plot function."""
        if x == "None" or y == "None":
            return go.Scatter(x=[], y=[], mode='markers', marker={'size':0})
        else:
            # Make plot with hovertext and add xlabel
            fig = go.Figure(data=[go.Scatter(x=self.four_digit_G.vs[x], y=self.four_digit_G.vs[y], text =self.four_digit_G.vs['title'],  mode='markers')])
            fig.update_layout(title=x+" vs. "+y, xaxis_title=x, yaxis_title=y)
            return fig


# We noW instantiate the object which contains both the network and the visualisation. 
labourNetwork = LabourNetwork()




##### People Like Me - Worker Map

jobs_to_codes = dict(zip(skill_scape_graph.vs['title'],skill_scape_graph.vs['name']))

# 3. Load in the matrix of person counts by occupation in each SA2 where they work (place of work in the 2016 census 
occ4DigitvsSA2POW2016 = pd.read_csv('data/Occ4DigitvsSA2POW2016.csv')
occ4DigitvsSA2POW2016.set_index('SA2', inplace=True)

class JobsMap():
    

    def __init__(self) -> None:
        self.SA2GeoJson = gpd.read_file('data/SA2GeoJson.gjson')


    def plot_jobs_on_map(self, occupation, POWorPUR = 'POW'):
        """Make a choropleth map of how many people from this occupation live there."""
        # Get the data
        occupation_code = str(int(jobs_to_codes[occupation]))
        if POWorPUR == 'POW':
            occupation_data = occ4DigitvsSA2POW2016[occupation_code]
        else:
            occupation_data = occ4DigitvsSA2PUR2016[occupation_code]
        occupation_data = occupation_data.dropna()

        self.SA2GeoJson['Counts'] = self.SA2GeoJson['SA2_MAIN16'].astype(int).map(occupation_data.to_dict())
        SA2GeoJson = self.SA2GeoJson.dropna()
        # Get the map
        fig = px.choropleth_mapbox(SA2GeoJson, geojson=SA2GeoJson.geometry,
                        locations=SA2GeoJson.index, 
                        color='Counts',
                        hover_name='SA2_NAME16', center={"lat": -34.908458, "lon": 138.629006},
                        hover_data=['SA2_MAIN16', 'SA2_NAME16', 'AREASQKM16', "Counts"], mapbox_style="carto-positron",
                                        zoom=8,)
        fig.update_layout(title=occupation+' by place of ')
        return fig

jobsMap = JobsMap()