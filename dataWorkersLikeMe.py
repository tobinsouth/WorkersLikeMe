import igraph as ig, numpy as np, pandas as pd

import plotly.graph_objs as go
# import base64 # For rendering images


import geopandas as gpd
import plotly.express as px


from dash import dcc, html
import pickle

# IMPORTANT: Load in two key datasets
# 1. The network of occupations linked by skills with metadata
skill_scape_graph = ig.Graph.Read_GraphML("data/skill_scape_graph.graphml")
nameMap = {str(int(c)):l for c, l in zip(skill_scape_graph.vs['name'], skill_scape_graph.vs['title'])}

# 2. Load in the matrix of person counts by occupation in each SA2 where they leave (place of usual residence) in the 2016 census 
occ4DigitvsSA2PUR2016 = pd.read_csv('data/Occ4DigitvsSA2PUR2016.csv')
occ4DigitvsSA2PUR2016.set_index('SA2', inplace=True)
totalOcc4Digit = occ4DigitvsSA2PUR2016.sum(axis=0).to_dict() # Sum over all areas


# 3. Load in all of the additional tables to display in the app
 
with open('data/scraped_occupations_tables.pickle', 'rb') as fp:
    all_occupation_tables = pickle.load(fp)


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
        # occupation_code = str(int(jobs_to_codes[occupation]))
        if occupation is None:
            return None
        print(occupation)
        occupation_code = str(int(occupation))
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
        fig.update_layout(title=str(occupation)+' by place of ')
        return fig

jobsMap = JobsMap()
empty_figure = {}



def make_all_data_tables(occupationCode):
    """Summary line.

    Extended description of function.

    Args:
        occupationCode (str)

    Returns:
        bool: Description of return value

    """

    thisOccData = all_occupation_tables[occupationCode]
    occName = nameMap[occupationCode]

    # Loop through the dataframes in the dictionary and create plotly figures for each one

    figures = []
    for title, table in thisOccData.items():
        if table is not None:
            if title == 'Employment Outlook':
                fig = px.line(data = table, x = 'Year', y = 'Number of Workers', title=title)
            elif title == 'Main Industries':
                fig = px.bar(data = table, x = 'Main Employing Industries', y = 'Industry (% share)', title=title)
            elif title == 'Education Level':
                table = table.melt(id_vars = 'Education Level', value_vars=[occName,'All Jobs Average'], var_name = 'Occupation', value_name = 'Percentage (%)')
                fig = px.bar(data = table, x = 'Education Level', y = 'Percentage (%)', title=title)
            elif title == 'Age Profile':
                table = table.melt(id_vars = 'Type of Qualification', value_vars=[occName,'All Jobs Average'], var_name = 'Occupation', value_name = 'Percentage (%)')
                fig = px.bar(data = table, x = 'Type of Qualification', y = 'Percentage (%)', color='Occupation', title=title)
            
            figures.append(html.Div(className = "six columns", children = dcc.Graph(figure=fig)))

    return html.Div(className = "row", children = figures)
