import time
time_start = time.time()

import os
import numpy as np
import pandas as pd
import sys
from scipy.stats.distributions import vonmises as vm
from math import pi

BASE_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
OUTPUT_PATH = os.path.join(BASE_PATH, 'Output')
NETWORK_PATH = os.path.join(BASE_PATH, 'Network')
ATTRACTIONS_FILE = os.path.join(NETWORK_PATH, 'attractions.csv')
TIME_PERIOD_FILE = os.path.join(NETWORK_PATH, 'TimePeriods.csv')
NODE_INFO_FILE = os.path.join(NETWORK_PATH, 'node_info.csv')
PEAK_FILE = os.path.join(NETWORK_PATH, 'peaks.csv')

def cdf(peaks, start, end):
    '''
    Computes the cdf between two time points for the given combination of Von Mises distributions
    '''
    out = 0
    for peak in peaks.index:
        contribution = peaks.loc[peak, 'Contribution']
        mu = peaks.loc[peak, 'Mean']*np.pi/12
        kappa = peaks.loc[peak, 'Concentration']
        out += contribution*(vm.cdf(end, kappa, loc = mu) - vm.cdf(start, kappa, loc = mu))
    return out

def convert_time_format(t):
    '''
    CONVERTS TIME!
    '''
    minute_map = {0: '00', 0.25: '15', 0.5: '30', 0.75: '45'}
    hour = str(int(t // 1) % 24)
    hour = (2 - len(hour))*'0' + hour
    minute = minute_map[t % 1]
    return "'{0}:{1}".format(hour, minute)

attractions = pd.read_csv(ATTRACTIONS_FILE, index_col = 0)
purposes = attractions.columns.tolist()

time_periods = pd.read_csv(TIME_PERIOD_FILE, index_col = 0)
peaks = pd.read_csv(PEAK_FILE)
node_info = pd.read_csv(NODE_INFO_FILE, index_col = 0)

breaks = []
for period in time_periods.index:
    start = time_periods.loc[period, 'Start']
    end = time_periods.loc[period, 'End']
    DTA = time_periods.loc[period, 'DTA']

    if DTA:
        breaks += list(np.arange(start, end, 0.25))

    else:
        breaks += [start]

N = len(node_info.index)
T = len(breaks)

total_trips = pd.Panel(np.zeros((T, N, N)), breaks, node_info.index, node_info.index)

trip_tables = {}
for purpose in purposes:
    
    starts = pi/12*np.array(breaks)
    ends = pi/12*np.array(breaks[1:] + [breaks[0] + 24])
    trip_tables[purpose] = pd.read_csv(os.path.join(OUTPUT_PATH, '{}_trip_table.csv'.format(purpose)), index_col = 0)

    total_origins = trip_tables[purpose].sum(1)
    total_destinations = trip_tables[purpose].sum(0)

    origin_nodes = total_origins[total_origins > 0].index.tolist()
    destination_nodes = total_destinations[total_destinations > 0].index.tolist()

    purpose_peaks = peaks[peaks['Purpose'] == purpose]

    for direction in list(range(2)):
        
        purpose_direction_peaks = purpose_peaks[purpose_peaks['Direction'] == direction]

        props = np.zeros_like(starts)
        for peak in purpose_direction_peaks.index:
            current_peak = purpose_direction_peaks.loc[peak]
            contribution = current_peak['Contribution']
            mean = current_peak['Mean']*pi/12
            concentration = current_peak['Concentration']
            peak_props = vm.cdf(ends, concentration, loc = mean) - vm.cdf(starts, concentration, loc = mean)
            props += contribution*peak_props

        for o_node in origin_nodes:
            for d_node in destination_nodes:
                daily_trips = trip_tables[purpose].loc[o_node, d_node]
                if not direction:
                    total_trips.ix[:, int(o_node), int(d_node)] += daily_trips*props
                else:
                    total_trips.ix[:, int(d_node), int(o_node)] += daily_trips*props

for period in time_periods.index:

    start = time_periods.loc[period, 'Start']
    end = time_periods.loc[period, 'End']
    DTA = time_periods.loc[period, 'DTA']

    if not DTA:
        total_trips[start, :, :].to_csv(os.path.join(BASE_PATH, r'TimePeriods\{}\trip_table.csv'.format(period)))

    else:
        period_trips = total_trips[np.arange(start, end, 0.25)]
        total_period_trips = period_trips.sum(0)
        trip_share = period_trips.sum(1).sum(0)
        trip_share /= trip_share.sum()

        INPUT_DEMAND_FILE = os.path.join(BASE_PATH, r'TimePeriods\{}\input_demand.csv'.format(period))
        INPUT_DEMAND_FILE_LIST_FILE = INPUT_DEMAND_FILE.replace('.csv', '_file_list.csv')

        input_demand_file_list = pd.read_csv(INPUT_DEMAND_FILE_LIST_FILE)

        node_list = total_period_trips.index.tolist()
        N = len(node_list)
        input_demand = pd.melt(total_period_trips)
        input_demand['from_zone_id'] = input_demand['Node']
        input_demand['to_zone_id'] = N*node_list
        input_demand['number_of_trips_demand_type1'] = input_demand['value']
        input_demand.set_index('from_zone_id')[['to_zone_id', 'number_of_trips_demand_type1']].to_csv(INPUT_DEMAND_FILE)

        for t in np.arange(0, 24, 0.25):
            input_demand_file_list.loc[0, convert_time_format(t)] = 0

        for t in np.arange(time_periods.loc[period, 'Start'], time_periods.loc[period, 'End'], 0.25):
            input_demand_file_list.loc[0, convert_time_format(t)] = trip_share[t]

        input_demand_file_list.set_index('scenario_no').to_csv(INPUT_DEMAND_FILE_LIST_FILE)

time_end = time.time()
runtime = round(time_end - time_start, 1)
print('Time of Day Modeling Complete in {} seconds'.format(runtime))