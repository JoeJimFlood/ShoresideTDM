import time
time_start = time.time()

import numpy as np
import pandas as pd
import os

BASE_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
OUTPUT_PATH = os.path.join(BASE_PATH, 'Output')
GENERATION_OUTPUT = os.path.join(OUTPUT_PATH, 'generation_output.csv')
ATTRACTIONS_FILE = os.path.join(BASE_PATH, r'Network\attractions.csv')
NODE_INFO_FILE = os.path.join(BASE_PATH, r'Network\node_info.csv')

def normalize(array):
    '''
    Divides an array by its sum

    Parameters
    ----------
    array (numpy.array):
        Array of values

    Returns
    -------
    normalized_array (numpy.array):
        `array` divided by its sum
    '''
    return array / array.sum()

nodes = pd.read_csv(GENERATION_OUTPUT, index_col = 0).fillna(0)
attractions = pd.read_csv(ATTRACTIONS_FILE, index_col = 0)
node_info = pd.read_csv(NODE_INFO_FILE, index_col = 0).fillna(0)
external_nodes = node_info[node_info['Type'] == 4]
external_nodes['Percent'] = normalize(external_nodes['Area'])

N = nodes.shape[0] #Number of nodes

for purpose in attractions.columns:

    attraction_share = normalize(nodes[purpose + 'Attractions'].values)
    attraction_shares = pd.DataFrame(np.vstack(N*[attraction_share]), nodes.index, nodes.index)
    trip_table = pd.DataFrame(np.zeros((N, N)), nodes.index, nodes.index)
    for node in trip_table.columns:
        trip_table[node] = nodes[purpose + 'Productions'] * attraction_shares[node]

    EE = attractions.loc[0, purpose]
    for onode in external_nodes.index:
        for dnode in external_nodes.index:
            ee_trips = EE*external_nodes.loc[onode, 'Percent']*external_nodes.loc[dnode, 'Percent']
            print(onode, dnode, ee_trips)
            trip_table.loc[onode, dnode] += ee_trips

    trip_table.to_csv(os.path.join(OUTPUT_PATH, purpose + '_trip_table.csv'))

time_end = time.time()
runtime = round(time_end - time_start, 1)
print('Trip Distribution Complete in {} seconds'.format(runtime))