"""
Preamble for most code and jupyter notebooks
@author: tobinsouth
@notebook date: 6 Oct 2021
"""

import numpy as np, pandas as pd, matplotlib.pyplot as plt, matplotlib as mpl, seaborn as sns
import math, string, re, pickle, json, os, sys, datetime, itertools
from collections import Counter
from tqdm import tqdm

import networkx as nx

import igraph as ig
with open('skill_scape_graph.pickle', 'rb') as f:
    skill_scape_graph = pickle.load(f)

skill_scape_graph.write_pajek('skill_scape_graph.pajek')


skill_scape_graph.vs[0]
# Get tuples of all edges


newg = ig.Graph()
newg.add_vertices(skill_scape_graph.vs['name'])
newg.add_edges(skill_scape_graph.get_edgelist())
newg.es['weight'] = skill_scape_graph.es['weight']
newg.vs['title'] = skill_scape_graph.vs['title']

newg.vs['x'] = skill_scape_graph.vs['x']
newg.vs['y'] = skill_scape_graph.vs['y']
newg.vs['unemployment'] = skill_scape_graph.vs['unemployment']
newg.vs['Females'] = skill_scape_graph.vs['Females']

newg.write_graphml('skill_scape_graph.graphml')



four_digit_G