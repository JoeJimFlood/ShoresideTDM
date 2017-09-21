import time
start_time = time.time()

import pandas as pd
import os

BASE_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
TIME_PERIOD_FILE = os.path.join(BASE_PATH, r'Network\TimePeriods.csv')
time_periods = pd.read_csv(TIME_PERIOD_FILE, index_col = 0)

for period in time_periods.index:
    time_period_path = os.path.join(BASE_PATH, r'TimePeriods\{}'.format(period))
    for f in os.listdir(time_period_path):
        os.remove(os.path.join(time_period_path, f))
    os.rmdir(time_period_path)
os.rmdir(os.path.join(BASE_PATH, 'TimePeriods'))

end_time = time.time()
run_time = end_time - start_time

print('Cleanup complete in {} seconds'.format(round(run_time, 1)))
