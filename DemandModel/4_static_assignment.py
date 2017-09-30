from __future__ import division
import time
start_time = time.time()

import numpy as np
import pandas as pd
import os
from collections import OrderedDict
import openmatrix as omx
import tables
import sys

BASE_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
SHORTEST_PATH_FILE = os.path.join(BASE_PATH, 'Network', 'shortest_paths.omx')
TIME_PERIOD_FILE = os.path.join(BASE_PATH, 'Network', 'TimePeriods.csv')
NODE_INFO_FILE = os.path.join(BASE_PATH, 'Network', 'node_info.csv')
LINK_FILE = os.path.join(BASE_PATH, 'DTA_Base', 'input_link.csv')
NODE_FILE = LINK_FILE.replace('link', 'node')
OUTPUT_FILE = os.path.join(BASE_PATH, 'Output', 'StaticLinkFlows.csv')

time_periods = pd.read_csv(TIME_PERIOD_FILE)
links = pd.read_csv(LINK_FILE, encoding = 'ISO-8859-1')
nodes = pd.read_csv(NODE_FILE)
node_info = pd.read_csv(NODE_INFO_FILE)

link_ids = links['link_id']
node_ids = np.array(node_info[node_info['Type'] > 0]['Node'])

#Read in shortest paths file
shortest_paths = {}
f = omx.open_file(SHORTEST_PATH_FILE, 'r')
order = list(f.mapping('Nodes').values())
for l in link_ids:
    values = np.array(f['Link{}'.format(l)])[order, :][:, order]
    shortest_paths[l] = pd.DataFrame(values,
                                     index = f.mapping('Nodes').keys(),
                                     columns = np.array(list(f.mapping('Nodes').keys())).astype(str))
shortest_paths = pd.Panel(shortest_paths)
#print('Shape: {}'.format(shortest_paths.shape))
#print('TEST1: {}'.format(shortest_paths[1295, 104, '530']))

#Read in trip tables
trip_tables = OrderedDict()
static_periods = []
for period in time_periods.index:
    static = not time_periods.loc[period, 'DTA']
    if static:
        name = time_periods.loc[period, 'Period']
        static_periods.append(name)
        TRIP_TABLE_FILE = r'D:\ShoresideTDM\TimePeriods\{}\trip_table.csv'.format(name)
        trip_tables[name] = pd.read_csv(TRIP_TABLE_FILE, index_col = 0).loc[node_ids, np.array(node_ids).astype(str)]
trip_tables = pd.Panel(trip_tables)

P = len(static_periods)
L = len(link_ids)
N = len(node_ids)

#Create 4-dimensional table (Static Periods x Links x Origin Nodes x Destination Nodes)
od_flows = pd.Panel4D(np.zeros((P, L, N, N)),
                      labels = static_periods,
                      items = link_ids,
                      major_axis = node_ids,
                      minor_axis = node_ids.astype(str))

#For each time period, if a link is in a shortest path between two nodes, put all of that time period's trip between said nodes in the 4D table
for period in static_periods:
    for l in link_ids:
        od_flows.ix[period, l, :, :] = trip_tables[period] * shortest_paths[l]
#print('TEST: {}'.format(od_flows.ix['MD', 1295, 104, '530']))

#Sum over origin and destination nodes to get flows on each link for each time period
link_flows = od_flows.sum(3).sum(2)
link_flows.to_csv(OUTPUT_FILE)

end_time = time.time()
runtime = round(end_time - start_time, 1)

print('Static Assignment complete in {} seconds'.format(runtime))