from __future__ import division
import time
start_time = time.time()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

BASE_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
TIME_LOG = os.path.join(BASE_PATH, 'TimeLog.txt')
OUTPUT_PATH = os.path.join(BASE_PATH, 'Output')
TIME_PERIOD_FILE = os.path.join(BASE_PATH, 'Network', 'TimePeriods.csv')
MAX_FC_FILE = os.path.join(BASE_PATH, 'Network', 'max_fc.txt')
LINKS_OF_INTEREST_FILE = os.path.join(BASE_PATH, 'Network', 'LinksOfInterest.csv')
STATIC_FLOWS_FILE = os.path.join(BASE_PATH, 'Output', 'StaticLinkFlows.csv')

sys.path.append(os.path.join(BASE_PATH, 'DemandModel'))
from tools import tod, spectral, util

time_periods = pd.read_csv(TIME_PERIOD_FILE, index_col = 0)
static_flows = pd.read_csv(STATIC_FLOWS_FILE, index_col = 0)
links = static_flows.index.tolist()
max_fc = int(open(MAX_FC_FILE).read().split('\n')[1])

links_of_interest = dict(pd.read_csv(LINKS_OF_INTEREST_FILE, index_col = 0).T)
for link_id in links_of_interest:
    links_of_interest[link_id] = tuple(links_of_interest[link_id])

#Define breaks
breaks = []
for period in time_periods.index:
    start = time_periods.loc[period, 'Start']
    end = time_periods.loc[period, 'End']
    dta = time_periods.loc[period, 'DTA']

    if dta:
        breaks += list(np.arange(start, end, 0.25))
    else:
        breaks += [start]

N = len(links)
T = len(breaks)

#Create data frame with flows at each time period specified in breaks
link_flows = pd.DataFrame(np.empty((N, T)), index = links, columns = breaks)

for period in time_periods.index:
    start = time_periods.loc[period, 'Start']
    end = time_periods.loc[period, 'End']
    dta = time_periods.loc[period, 'DTA']

    if dta:
        LINK_FILE = os.path.join(BASE_PATH, r'TimePeriods\{}\input_Link.csv'.format(period))
        FLOW_FILE = os.path.join(BASE_PATH, r'TimePeriods\{}\output_LinkTDMOE.csv'.format(period))
        links = pd.read_csv(LINK_FILE, encoding = 'ISO-8859-1')[['link_id', 'from_node_id', 'to_node_id']]
        flows = pd.read_csv(FLOW_FILE, encoding = 'ISO-8859-1', index_col = False)

        links['od'] = list(zip(links['from_node_id'], links['to_node_id']))
        links = links.set_index('od')

        flows['od'] = list(zip(flows['from_node_id'], flows['to_node_id']))
        flows['link_id'] = flows['od'].map(links['link_id'])
        flows['quarter_hour'] = flows['timestamp_in_min'].apply(tod.quarterhourize)

        flowcol = 'link_in_volume_number_of_veh'
        grouped_data = flows[['link_id', 'quarter_hour', flowcol]].groupby(['link_id', 'quarter_hour']).sum()[flowcol].reset_index()
        grouped_data = grouped_data.pivot(index = 'link_id', columns = 'quarter_hour', values = flowcol)
        
        period_breaks = list(np.arange(start, end, 0.25))
        link_flows[period_breaks] = grouped_data[period_breaks]

    else:
        link_flows[start] = static_flows[period]

#Define dictionary for profiles and the maximum number of Fourier coefficients to use
dists = {}
for link_id in links_of_interest.keys():
    try:
        K = max_fc
        proceed = False
        while not proceed:
            try:
                dists[link_id] = spectral.Profile.from_bins(np.array(link_flows.loc[link_id]), np.array(link_flows.columns), K+1)
                proceed = True
            except OverflowError:
                K -= 1
    except KeyError:
        print('KeyError with Link{}'.format(link_id))
        continue

#Plot and save results
font = 'Perpetua'
fs = 32

for link in links_of_interest:
    title = links_of_interest[link][0]
    util.plot_link(dists, link_flows, link, title, fs, font, os.path.join(OUTPUT_PATH, 'Plots', '{}.png'.format(title)))

util.plot_links(dists, [1295, 1294, 1321, 1320], links_of_interest, 15000, 'Bridge Crossings',
                fs, font, os.path.join(OUTPUT_PATH, r'Plots\BridgeCrossings.png'))
util.plot_links(dists, [1273, 1272, 1321, 1320], links_of_interest, 17000, 'To/From CBD',
                fs, font, os.path.join(OUTPUT_PATH, r'Plots\ToFromCBD.png'))
util.plot_links(dists, [1319, 1318, 1233, 1232], links_of_interest, 17000, 'CBD Entrances',
                fs, font, os.path.join(OUTPUT_PATH, r'Plots\CBDEntrances.png'))
util.plot_links(dists, [1238, 1239, 1315, 1314], links_of_interest, 20000, 'CBD Freeways',
                fs, font, os.path.join(OUTPUT_PATH, r'Plots\CBDFreeways.png'))

outdata = util.pack(dists, max_fc)
outdata.to_csv(os.path.join(OUTPUT_PATH, 'Profiles.csv'))

end_time = time.time()
runtime = round(end_time - start_time, 1)

print('Spectral Post-Processing Complete in {} seconds'.format(runtime))

logfile = open(TIME_LOG, 'a')
logfile.write('\nSpectral Postprocessing: {}'.format(runtime))
logfile.close()