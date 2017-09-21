import time
start_time = time.time()

import numpy as np
import pandas as pd
import os
from collections import OrderedDict
import openmatrix as omx
import sys

SHORTEST_PATH_FILE = r'D:\ShoresideTDM\Network\shortest_paths.omx'
TIME_PERIOD_FILE = r'D:\ShoresideTDM\Network\TimePeriods.csv'
LINK_FILE = r'D:\ShoresideTDM\DTA_Base\input_link.csv'
NODE_FILE = LINK_FILE.replace('link', 'node')
NODE_INFO_FILE = r'D:\ShoresideTDM\Network\node_info.csv'

time_periods = pd.read_csv(TIME_PERIOD_FILE)
links = pd.read_csv(LINK_FILE, encoding = 'ISO-8859-1')
nodes = pd.read_csv(NODE_FILE)
node_info = pd.read_csv(NODE_INFO_FILE)

link_ids = links['link_id']
node_ids = np.array(node_info[node_info['Type'] > 0]['Node'])

shortest_paths = {}
if sys.version[0] == '2':
    f = omx.openFile(SHORTEST_PATH_FILE, 'r')
elif sys.version[0] == '3':
    f = omx.open_file(SHORTEST_PATH_FILE, 'r')
for l in link_ids:
    shortest_paths[l] = pd.DataFrame(np.array(f['Link{}'.format(l)]),
                                     index = f.mapping('Nodes').keys(),
                                     columns = np.array(list(f.mapping('Nodes').keys())).astype(str))
f.close()

shortest_paths = pd.Panel(shortest_paths)

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

od_flows = pd.Panel4D(np.zeros((P, L, N, N)),
                      labels = static_periods,
                      items = link_ids,
                      major_axis = node_ids,
                      minor_axis = node_ids.astype(str))

for period in static_periods:
    for l in link_ids:
        od_flows.ix[period, l, :, :] = trip_tables[period] * shortest_paths[l]

link_flows = od_flows.sum(3).sum(2)
link_flows.to_csv(r'D:\ShoresideTDM\Output\StaticLinkFlows.csv')

end_time = time.time()
runtime = round(end_time - start_time, 1)

print('Static Assignment complete in {} seconds'.format(runtime))