import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import stp11 as stp
#import spectranspo as stp
import os

BASE_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
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

K = 5
inbound_skyrider = stp.TimeDist.from_bins(np.array(link_flows.loc[1321]), np.array(link_flows.columns), 4)
inbound_skyrider.plot(1440, pdf = False, label = 'Skyrider')
eb50 = stp.TimeDist.from_bins(np.array(link_flows.loc[1295]), np.array(link_flows.columns), 4)
eb50.plot(1550, pdf = False, label = '50 Street')
plt.xlim(0, 24)
plt.title('Westbound Bridges')
plt.legend(loc = 'best')
plt.ylabel('Flow (Vehicles per Hour)')
plt.show()

print('Spectral Post-Processing Complete')