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

print('Creating Time-specific trip tables')

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

        

        

print('Done')