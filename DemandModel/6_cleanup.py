import time
start_time = time.time()

import pandas as pd
import os

BASE_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
TIME_LOG = os.path.join(BASE_PATH, 'TimeLog.txt')
TIME_PERIOD_FILE = os.path.join(BASE_PATH, r'Network\TimePeriods.csv')
time_periods = pd.read_csv(TIME_PERIOD_FILE, index_col = 0)

#Remove all time period folders, as they are very large
for period in time_periods.index:
    time_period_path = os.path.join(BASE_PATH, r'TimePeriods\{}'.format(period))
    for f in os.listdir(time_period_path):
        os.remove(os.path.join(time_period_path, f))
    os.rmdir(time_period_path)
os.rmdir(os.path.join(BASE_PATH, 'TimePeriods'))

end_time = time.time()
runtime = round(end_time - start_time, 1)

print('Cleanup complete in {} seconds'.format(runtime))

logfile = open(TIME_LOG, 'a')
logfile.write('\nCleanup: {}'.format(runtime))

import datetime
end_time = datetime.datetime.now()
last_line = r'===/|\===Shoreside CBD TDM Run End: {}===/|\==='.format(end_time.strftime('%d.%m.%y.%H.%M.%S'))
logfile.write('\n\n' + len(last_line)*'-' + '\n')
logfile.write(last_line)
logfile.close()