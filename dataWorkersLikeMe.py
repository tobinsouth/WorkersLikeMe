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
        occupation_code = occupation
        occName = nameMap[occupation_code]
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
                                        zoom=6,)
        fig.update_layout(title='Place of '+('Work' if POWorPUR=='POW' else 'Residence') + ' of ' + occName)
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
    if occupationCode not in all_occupation_tables:
        return None

    thisOccData = all_occupation_tables[occupationCode]
    occName = nameMap[occupationCode]

    # Loop through the dataframes in the dictionary and create plotly figures for each one

    rows, columns = [], []
    for i, (title, table) in enumerate(thisOccData.items()):
        if table is not None:
            if title == 'Employment Outlook':
                fig = px.line(table, x = 'Year', y = 'Number of Workers', title=title)
            elif title == 'Main Industries':
                fig = px.bar(table, x = 'Main Employing Industries', y = 'Industry (% share)', title=title)
            elif title == 'Education Level':
                occNameVal = table.columns[1]
                table = table.melt(id_vars = 'Type of Qualification', value_vars=[occNameVal,'All Jobs Average'], var_name = 'Occupation', value_name = 'Percentage (%)')
                fig = px.bar(table, x = 'Type of Qualification', y = 'Percentage (%)', color='Occupation', barmode="group", title=title)
            elif title == 'Age Profile':
                occNameVal = table.columns[1]
                table = table.melt(id_vars = 'Age Bracket', value_vars=[occNameVal,'All Jobs Average'], var_name = 'Occupation', value_name = 'Percentage (%)')
                fig = px.bar(table, x = 'Age Bracket', y = 'Percentage (%)', color='Occupation', title=title, barmode="group")

            columns.append(html.Div(className = "six columns", children = dcc.Graph(figure=fig)))
            if i % 2 == 1:
                rows.append(html.Div(className = "row", children = columns))
                columns = []

    return html.Div(className = "row", children = rows)
