import time
time_start = time.time()

import numpy as np
import pandas as pd
import os

BASE_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
NETWORK_PATH = os.path.join(BASE_PATH, 'Network')
OUTPUT_PATH = os.path.join(BASE_PATH, 'Output')

NODE_INFO_FILE = os.path.join(NETWORK_PATH, 'node_info.csv')
ATTRACTION_FILE = os.path.join(NETWORK_PATH, 'attractions.csv')
GENERATION_OUTPUT_FILE = os.path.join(OUTPUT_PATH, 'generation_output.csv')

#Read in node and attraction information
nodes = pd.read_csv(NODE_INFO_FILE, index_col = 0)
attractions = pd.read_csv(ATTRACTION_FILE, index_col = 0)

#Compute productions from total attractions of each purpose
productions = pd.DataFrame(np.zeros_like(attractions.values), index = attractions.index, columns = attractions.columns)
productions.loc[4] = attractions.sum()

#Create dictionary of total areas for area types
area_map = {0: np.inf}
for type in range(1, 5):
    node_subset = nodes[nodes['Type'] == type]
    area_map[type] = node_subset['Area'].sum()

#Distribute productions and attractions according to area shares within node purposes
nodes['TypeShare'] = nodes['Area'] / nodes['Type'].map(area_map)
for purpose in productions.columns:
    nodes[purpose + 'Productions'] = nodes['TypeShare'] * nodes['Type'].map(productions[purpose])
    nodes[purpose + 'Attractions'] = nodes['TypeShare'] * nodes['Type'].map(attractions[purpose])

#Write output to file
nodes.to_csv(GENERATION_OUTPUT_FILE)

time_end = time.time()
runtime = round(time_end - time_start, 1)
print('Trip Generation Complete in {} seconds'.format(runtime))