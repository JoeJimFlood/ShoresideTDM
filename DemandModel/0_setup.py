import time
start_time = time.time()

import pandas as pd
import os
from shutil import copy

BASE_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
DEMAND_MODEL_PATH = os.path.join(BASE_PATH, 'DemandModel')
DTA_BASE_PATH = os.path.join(BASE_PATH, 'DTA_Base')
TIME_PERIOD_FILE = os.path.join(BASE_PATH, 'Network/TimePeriods.csv')
BATCH_FILE = os.path.join(DEMAND_MODEL_PATH, 'Model.bat')

DTALite_PATH = r'D:\DTALite'

#Write batch lines executing each step of the model
batch_lines = [r'python 1_generation.py'.format(DEMAND_MODEL_PATH),
               r'python 2_distribution.py'.format(DEMAND_MODEL_PATH),
               r'python 3_tod.py'.format(DEMAND_MODEL_PATH),
               r'python 4_static_assignment.py'.format(DEMAND_MODEL_PATH)]

#Create directory for each time period
os.mkdir(os.path.join(BASE_PATH, 'TimePeriods'))
time_periods = pd.read_csv(TIME_PERIOD_FILE, index_col = 0)
for period in time_periods.index:
    time_period_path = os.path.join(BASE_PATH, 'TimePeriods', period)
    os.mkdir(time_period_path)
    dta = time_periods.loc[period, 'DTA']
    #Copy DTALite files into DTA time period directories
    if dta:
        copy(os.path.join(DTALite_PATH, 'DTALite.exe'), time_period_path)
        for f in os.listdir(DTA_BASE_PATH):
            copy(os.path.join(DTA_BASE_PATH, f), time_period_path)
        batch_lines.append(r'cd {0}\TimePeriods\{1}'.format(BASE_PATH, period))
        batch_lines.append(r'DTALite.exe'.format(BASE_PATH, period))

batch_lines.append(r'cd {}\DemandModel'.format(BASE_PATH))
batch_lines.append(r'python 5_spectral_post_processing.py'.format(DEMAND_MODEL_PATH))
batch_lines.append(r'python 6_cleanup.py'.format(DEMAND_MODEL_PATH))
batch_lines.append('pause')

#Write batch file
f = open(BATCH_FILE, 'w')
f.write('\n'.join(batch_lines))
f.close()

end_time = time.time()
run_time = end_time - start_time

print('Setup complete in {} seconds'.format(round(run_time, 1)))