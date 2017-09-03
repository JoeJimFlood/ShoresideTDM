import time
start_time = time.time()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import stp11 as stp
#import spectranspo as stp
import os

BASE_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
OUTPUT_PATH = os.path.join(BASE_PATH, 'Output')
TIME_PERIOD_FILE = os.path.join(BASE_PATH, r'Network\TimePeriods.csv')
STATIC_FLOWS_FILE = os.path.join(BASE_PATH, r'Output\StaticLinkFlows.csv')

def quarterhourize(minute):
    '''
    Converts a minute since midnight to a quarter hour since midnight. Rounds down.

    Parameters
    ----------
    minute (int):
        Number of minutes since midnight

    Returns
    -------
    quarter_hour (float):
        Time of day to the nearest quarter-hour (0.0, 0.25, 0.5, 0.75, 1.0, ..., 23.5, 23.75)
    '''
    hour = (minute // 60) % 24
    minute_in_hour = minute % 60
    proportion_of_hour = (minute_in_hour // 15) / 4
    quarter_hour = hour + proportion_of_hour
    
    return quarter_hour

time_periods = pd.read_csv(TIME_PERIOD_FILE, index_col = 0)
static_flows = pd.read_csv(STATIC_FLOWS_FILE, index_col = 0)

links = static_flows.index.tolist()

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
        flows['quarter_hour'] = flows['timestamp_in_min'].apply(quarterhourize)

        flowcol = 'link_in_volume_number_of_veh'
        grouped_data = flows[['link_id', 'quarter_hour', flowcol]].groupby(['link_id', 'quarter_hour']).sum()[flowcol].reset_index()
        grouped_data = grouped_data.pivot(index = 'link_id', columns = 'quarter_hour', values = flowcol)
        
        period_breaks = list(np.arange(start, end, 0.25))
        link_flows[period_breaks] = grouped_data[period_breaks]

    else:
        link_flows[start] = static_flows[period]


links_of_interest = {1321: ('Inbound Skyrider', '#c0c0c0', '-'),
                     1320: ('Outbound Skyrider', '#c0c0c0', '--'),
                     1295: ('Eastbound 50 Street Bridge', '#8040a0', '-'),
                     1294: ('Westbound 50 Street Bridge', '#8040a0', '--'),
                     1273: ('Inbound Eastern Bank Freeway', '#008040', '-'),
                     1272: ('Outbound Eastern Bank Freeway', '#008040', '--')}

dists = {}

max_fc = 3

for link_id in links_of_interest.keys():
    K = max_fc
    proceed = False
    while not proceed:
        try:
            dists[link_id] = stp.TimeDist.from_bins(np.array(link_flows.loc[link_id]), np.array(link_flows.columns), K+1)
            proceed = True
        except OverflowError:
            K -= 1

def pack(dists, K, dtype = np.float16):
    global OUTPUT_PATH

    N = len(dists)

    outdata_columns = ['L0']
    for k in range(1, K+1):
        outdata_columns += ['L%dre'%(k), 'L%dim'%(k)]

    outdata = pd.DataFrame(np.zeros((N, 2*K+1), dtype), index = dists.keys(), columns = outdata_columns)

    for link_id in dists.keys():
        outdata.loc[link_id, 'L0'] = dtype(np.real(dists[link_id].L.c[0]) + np.log(dists[link_id].total))
        for k in range(1, K+1):
            Lk = dists[link_id].L.c[k]
            outdata.loc[link_id, 'L%dre'%(k)] = dtype(np.real(Lk))
            outdata.loc[link_id, 'L%dim'%(k)] = dtype(np.imag(Lk))

    outdata.index.name = 'LinkID'

    return outdata

outdata = pack(dists, max_fc)
outdata.to_csv(os.path.join(OUTPUT_PATH, 'Distributions.csv'))

def plot_links(dists, link_ids, ymax, title, font_size, font, fp = None):
    '''
    Plots selected links with the selected titles
    '''
    plt.figure(figsize = (16, 9))

    for i in range(0, 25, 3):
        plt.plot([i, i], [0, ymax], color = 'k')
    
    for link_id in link_ids:
        dists[link_id].plot(1440, pdf = False, linewidth = 3,
                            color = links_of_interest[link_id][1],
                            linestyle = links_of_interest[link_id][2],
                            label = links_of_interest[link_id][0])

    xticks = list(range(25))
    xlabels = ['12 AM', '', '', '3 AM', '', '', '6 AM', '', '', '9 AM', '', '',
               '12 PM', '', '', '3 PM', '', '', '6 PM', '', '', '9 PM', '', '',
               '12 AM']

    plt.xlim(0, 24)
    plt.ylim(0, ymax)
    plt.xticks(xticks, xlabels, fontsize = font_size, fontname = font, rotation = 5)
    plt.ylabel('Flow (Vehicles per Hour)', fontsize = font_size, fontname = font)
    plt.yticks(fontsize = font_size, fontname = font)

    plt.grid(True)
    plt.title(title, fontsize = font_size, fontname = font, va = 'bottom')
    
    legend = plt.legend(loc = 'upper left')
    for text in legend.get_texts():
        text.set_fontname(font)
        text.set_size(font_size)
    
    if fp:
        plt.savefig(fp)
        plt.clf()
    else:
        plt.show()

font = 'Perpetua'
fs = 32
plot_links(dists, [1295, 1294, 1321, 1320], 15000, 'Bridge Crossings', fs, font, os.path.join(OUTPUT_PATH, r'Plots\BridgeCrossings.png'))
plot_links(dists, [1273, 1272, 1321, 1320], 17000, 'To/From CBD', fs, font, os.path.join(OUTPUT_PATH, r'Plots\ToFromCBD.png'))

end_time = time.time()
run_time = end_time - start_time

print('Spectral Post-Processing Complete in {} seconds'.format(round(run_time, 1)))