import time
start_time = time.time()

import numpy as np
import pandas as pd
import os

SHORTEST_PATH_FILE = r'D:\ShoresideTDM\Network\shortest_paths.txt'
TIME_PERIOD_FILE = r'D:\ShoresideTDM\Network\TimePeriods.csv'
LINK_FILE = r'D:\ShoresideTDM\DTA_Base\input_link.csv'

time_periods = pd.read_csv(TIME_PERIOD_FILE)
shortest_paths = open(SHORTEST_PATH_FILE, 'r').read().split('\n')
links = pd.read_csv(LINK_FILE, encoding = 'ISO-8859-1')

trip_table = {}
static_periods = []

for period in time_periods.index:
    static = not time_periods.loc[period, 'DTA']
    if static:
        name = time_periods.loc[period, 'Period']
        static_periods.append(name)
        TRIP_TABLE_FILE = r'D:\ShoresideTDM\TimePeriods\{}\trip_table.csv'.format(name)
        trip_table[name] = pd.read_csv(TRIP_TABLE_FILE, index_col = 0)

link_flows = pd.DataFrame(np.zeros((len(links.index), len(static_periods)), dtype = np.float64), index = links['link_id'], columns = static_periods)

for path in shortest_paths:
    (od, path_links) = path.split(': ')
    (origin, destination) = od.split(' -> ')
    path_links = path_links.split(', ')

    print(od)

    for period in static_periods:
        for link in path_links:
            link_flows.loc[int(link), period] += trip_table[period].loc[int(origin), destination]

raise Exception

##for onode in trip_table[name].index:
#    for dnode in trip_table[name].columns:
#        if trip_table[static_periods[0]].loc[onode, dnode]:

#            print('{0} \u2192 {1}'.format(onode, dnode))
            
#            origin = Shoreside.find_node(onode)
#            destination = Shoreside.find_node(int(dnode))
#            route = Shoreside.get_shortest_route(origin, destination)
            
#            for l in route:
#                for period in static_periods:
#                    link_flows.loc[l.id, period] += trip_table[period].loc[onode, dnode]

#        #link_flows[period] = flows

link_flows.to_csv(r'D:\ShoresideTDM\Output\StaticLinkFlows.csv')

end_time = time.time()
runtime = round(end_time - start_time, 1)

print('Static Assignment complete in {} seconds'.format(runtime))