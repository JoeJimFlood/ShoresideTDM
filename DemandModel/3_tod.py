import time
time_start = time.time()

import os
import numpy as np
import pandas as pd
import sys
from scipy.stats.distributions import vonmises as vm
from math import pi

BASE_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
TIME_LOG = os.path.join(BASE_PATH, 'TimeLog.txt')
OUTPUT_PATH = os.path.join(BASE_PATH, 'Output')
NETWORK_PATH = os.path.join(BASE_PATH, 'Network')
ATTRACTIONS_FILE = os.path.join(NETWORK_PATH, 'attractions.csv')
TIME_PERIOD_FILE = os.path.join(NETWORK_PATH, 'TimePeriods.csv')
NODE_INFO_FILE = os.path.join(NETWORK_PATH, 'node_info.csv')
PEAK_FILE = os.path.join(NETWORK_PATH, 'peaks.csv')

DTA_START_UP_TIME = 1 #Time to set up DTA in hours

sys.path.append(os.path.join(BASE_PATH, 'DemandModel'))
from tools import tod

attractions = pd.read_csv(ATTRACTIONS_FILE, index_col = 0)
purposes = attractions.columns.tolist()
time_periods = pd.read_csv(TIME_PERIOD_FILE, index_col = 0)
peaks = pd.read_csv(PEAK_FILE)
node_info = pd.read_csv(NODE_INFO_FILE, index_col = 0)

#Define start times of each sub-period. Start time for static periods, and 15-minute increments for dynamic periods
breaks = {}
for period in time_periods.index:
    start = time_periods.loc[period, 'Start']
    end = time_periods.loc[period, 'End']
    DTA = time_periods.loc[period, 'DTA']

    if DTA:
        breaks[period] = list(np.arange(start - DTA_START_UP_TIME, end, 0.25))

    else:
        breaks[period] = [start]

N = len(node_info.index)

#Create the total number of trips within each sub-interval in each time period
total_trips = {}
for period in time_periods.index:
    T = len(breaks[period])
    total_trips[period] = pd.Panel(np.zeros((T, N, N)), breaks[period], node_info.index, node_info.index)

trip_tables = {}
for period in time_periods.index:
    
    trip_tables[period] = {}
    DTA = time_periods.loc[period, 'DTA']

    for purpose in purposes:
    
        #Convert start and end times of each sub-period to angles of earth's rotation
        if DTA:
            starts = pi/12*np.array(breaks[period])
            ends = pi/12*np.array(breaks[period][1:] + [breaks[period][-1] + 0.25])
        else:
            starts = pi/12*np.array(time_periods.loc[period, ['Start']])
            ends = pi/12*np.array(time_periods.loc[period, ['End']])
            if ends[0] < starts[0]:
                ends += 2*pi
        trip_tables[purpose] = pd.read_csv(os.path.join(OUTPUT_PATH, '{}_trip_table.csv'.format(purpose)), index_col = 0)

        #Sum total origins and destinations
        total_origins = trip_tables[purpose].sum(1)
        total_destinations = trip_tables[purpose].sum(0)

        origin_nodes = total_origins[total_origins > 0].index.tolist()
        destination_nodes = total_destinations[total_destinations > 0].index.tolist()

        #Read in peaks for each purpose
        purpose_peaks = peaks[peaks['Purpose'] == purpose]

        for direction in list(range(2)):
        
            purpose_direction_peaks = purpose_peaks[purpose_peaks['Direction'] == direction]

            #Create profiles for each purpose/direction
            props = np.zeros_like(starts)
            for peak in purpose_direction_peaks.index:
                current_peak = purpose_direction_peaks.loc[peak]
                contribution = current_peak['Contribution']
                mean = current_peak['Mean']*pi/12
                concentration = current_peak['Concentration']
                peak_props = vm.cdf(ends, concentration, loc = mean) - vm.cdf(starts, concentration, loc = mean)
                props += contribution*peak_props

            #Apply profiles to create time-specific trip tables
            for o_node in origin_nodes:
                for d_node in destination_nodes:
                    daily_trips = trip_tables[purpose].loc[o_node, d_node]
                    try:
                        if direction: #Departure trips
                            total_trips[period].ix[:, int(o_node), int(d_node)] += daily_trips*props
                        else: #Return trips
                            total_trips[period].ix[:, int(d_node), int(o_node)] += daily_trips*props
                    except KeyError:
                        continue

for period in time_periods.index:

    start = time_periods.loc[period, 'Start']
    end = time_periods.loc[period, 'End']
    DTA = time_periods.loc[period, 'DTA']

    #Save trip tables for static periods
    if not DTA:
        total_trips[period][start].to_csv(os.path.join(BASE_PATH, r'TimePeriods\{}\trip_table.csv'.format(period)))

    #Update time-dependent profile for dynamic periods
    else:
        
        period_trips = total_trips[period]
        total_period_trips = period_trips.sum(0)
        trip_share = period_trips.sum(1).sum(0)
        trip_share /= trip_share.sum()

        INPUT_DEMAND_FILE = os.path.join(BASE_PATH, r'TimePeriods\{}\input_demand.csv'.format(period))
        INPUT_DEMAND_FILE_LIST_FILE = INPUT_DEMAND_FILE.replace('.csv', '_file_list.csv')

        input_demand_file_list = pd.read_csv(INPUT_DEMAND_FILE_LIST_FILE)

        #For each origin-destination pair, update the number of trips in the input file
        node_list = total_period_trips.index.tolist()
        N = len(node_list)
        input_demand = pd.melt(total_period_trips)
        input_demand['from_zone_id'] = input_demand['Node']
        input_demand['to_zone_id'] = N*node_list
        input_demand['number_of_trips_demand_type1'] = input_demand['value'].round(0)
        input_demand.set_index('from_zone_id')[['to_zone_id', 'number_of_trips_demand_type1']].to_csv(INPUT_DEMAND_FILE)

        #Update time-dependent profile
        input_demand_file_list['start_time_in_min'] = int((time_periods.loc[period, 'Start'] - DTA_START_UP_TIME)*60)
        input_demand_file_list['end_time_in_min'] = int(time_periods.loc[period, 'End']*60)

        #Set all 15-minute periods to zero
        for t in np.arange(0, 24, 0.25):
            input_demand_file_list.loc[0, tod.convert_time_format(t)] = 0

        #Set desired 15-minute periods
        for t in np.arange(time_periods.loc[period, 'Start'] - DTA_START_UP_TIME, time_periods.loc[period, 'End'], 0.25):
            input_demand_file_list.loc[0, tod.convert_time_format(t)] = trip_share[t]

        input_demand_file_list.set_index('scenario_no').to_csv(INPUT_DEMAND_FILE_LIST_FILE)

time_end = time.time()
runtime = round(time_end - time_start, 1)
print('Time of Day Modeling Complete in {} seconds'.format(runtime))

logfile = open(TIME_LOG, 'a')
logfile.write('\nTime of Day: {}'.format(runtime))
logfile.close()