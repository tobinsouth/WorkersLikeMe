"""
This script will collect the list of current ANZSCO classification jobs listed on the [JobOutlook government website](joboutlook.gov.au) and will scrape the job description and job metadata for each job.

This new data will be saved to a json file and will be used to update the node metadata for the skillscape jobs graph.
"""
import numpy as np, pandas as pd, matplotlib.pyplot as plt, matplotlib as mpl, seaborn as sns
import math, string, re, pickle, json, os, sys, datetime, itertools
from collections import Counter
from tqdm import tqdm

from bs4 import BeautifulSoup
import requests

jobOutlookURL = 'https://joboutlook.gov.au'

# Get links to every job.
soup = BeautifulSoup(requests.get(jobOutlookURL+'/occupations/').text, 'html.parser')
occupationsContainer = soup.find_all("section", class_="occupations-container")[0]

all_occupations = {}
for topic in occupationsContainer.find_all("div", class_="topic-item"):
    topic = topic.find('a')
    href = topic.get('href')
    title = topic.text
    all_occupations[title] = href

#####################################################################
# Get all the occupations overview data.
#####################################################################
all_occupations_detailed = {}
for title, href in tqdm(all_occupations.items()):
    soup = BeautifulSoup(requests.get(jobOutlookURL + href).text, 'html.parser')
    lead = soup.find('div', class_="col m-2").find('div', class_="col-md-9 col-print-9").find_all("p", class_="lead")[0].text.rstrip().lstrip()
    all_fast_facts = soup.find('div', class_="fast-facts").find_all('div',class_='snapshot-info')
    for fast_fact in all_fast_facts:
        btn_tag = fast_fact.find('button')
        if btn_tag:
            btn_tag.decompose()
    fast_facts = {fast_fact.find('span', class_="snapshot-title").text.lstrip().rstrip():fast_fact.find('span', class_="snapshot-data").text.lstrip().rstrip() for fast_fact in all_fast_facts}
    all_occupations_detailed[title] = {'lead':lead, 'fast_facts':fast_facts, 'href':href}

# Get occupation code
for title, data in all_occupations_detailed.items():
    code = data['href'].split('=')[-1]
    all_occupations_detailed[title]['code'] = code

# Save as JSON
with open('data/scraped_occupations_details.json', 'w') as fp:
    json.dump(all_occupations_detailed, fp)


#####################################################################
###### This section will now update the skill_scape_graph.json file with the latest data.
#####################################################################

# Read in json again
with open('data/scraped_occupations_details.json', 'r') as fp:
    all_occupations_detailed = json.load(fp)

# Read in the graph
import igraph as ig
skill_scape_graph = ig.Graph.Read_GraphML("data/skill_scape_graph.graphml")

# Clear old parameters
for attribute in skill_scape_graph.vs.attributes():
    if attribute not in ['name', 'title', 'x', 'y']:
        del skill_scape_graph.vs[attribute]

# This will take every parameter for each occupation and create a mapping from the ANZSCO code. 
parameter_mappings = {k:{} for k in ['Lead', 'Weekly Pay', 'Future Growth', 'Employment Size', 'Skill level rating', 'Full-Time Share', 'Average full-time', 'Average age', 'Gender Share', 'Weekly Pay Numeric', 'Future Growth', 'Employment Size Numeric', 'Skill level rating', 'Full-Time Share Numeric', 'Average full-time Numeric', 'Average age Numeric', 'Gender Share Numeric']}
for occ_title, details in all_occupations_detailed.items():
    # if len(details['code']) == 4:
    ANZSCOcode = int(details['code'])
    parameter_mappings['Lead'][ANZSCOcode] = details['lead']
    for key, value in details['fast_facts'].items():
        if key in parameter_mappings:
            parameter_mappings[key][ANZSCOcode] = value
            # Check for numeric values and extract
            numeric = re.findall('[0-9]+', value)
            if numeric:
                parameter_mappings[key+ ' Numeric'][ANZSCOcode] = int(''.join(numeric))

for parameter, mapping in parameter_mappings.items():
    skill_scape_graph.vs[parameter] = [mapping.get(int(code)) for code in skill_scape_graph.vs['name']]

# Save updated graph
skill_scape_graph.write_graphml("data/skill_scape_graph.graphml")


#####################################################################
#### We will now collect extra data for each occupation based on the other tabs in job outlook.
#####################################################################
with open('data/scraped_occupations_details.json', 'r') as fp:
    all_occupations_detailed = json.load(fp)

all_occupation_tables = {}
for occ_title, details in tqdm(all_occupations_detailed.items()):
    code = details['code']
    if len(code) == 4:
        href = details['href']
        soup = BeautifulSoup(requests.get(jobOutlookURL + href).text, 'html.parser')
        tabs = soup.find('div', id="myTabContent")
        prospects = tabs.find('div', id="prospects")
        cards = prospects.find_all('div', class_="card")
        all_occupation_tables[code] = {}
        for card in cards:
            header = card.find('div', class_="card-header").text.lstrip().rstrip()
            table = card.find('div', class_="data-table")
            pdtable = pd.read_html(str(table))[0]
            all_occupation_tables[code][header] = pdtable

# Save as pickle since we're mixing dataframes and json
with open('data/scraped_occupations_tables.pickle', 'wb') as fp:
    pickle.dump(all_occupation_tables, fp)
