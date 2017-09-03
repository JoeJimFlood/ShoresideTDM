import pandas as pd
import os
from shutil import copy
from subprocess import Popen, call

BASE_PATH = os.path.split(os.path.realpath(__file__))[0]
DEMAND_MODEL_PATH = os.path.join(BASE_PATH, 'DemandModel')
DTA_BASE_PATH = os.path.join(BASE_PATH, 'DTA_Base')
TIME_PERIOD_FILE = os.path.join(BASE_PATH, 'Network/TimePeriods.csv')
BATCH_FILE = os.path.join(BASE_PATH, 'ShoresideTDM.bat')

DTALite_PATH = r'D:\DTALite'

batch_lines = ['cd {}\DemandModel'.format(BASE_PATH),
               'python 1_generation.py',
               'python 2_distribution.py',
               'python 3_tod.py',
               'python 4_static_assignment.py']

time_periods = pd.read_csv(TIME_PERIOD_FILE, index_col = 0)
for period in time_periods.index:
    time_period_path = os.path.join(BASE_PATH, r'TimePeriods\{}'.format(period))
    os.mkdir(time_period_path)
    dta = time_periods.loc[period, 'DTA']
    if dta:
        copy(os.path.join(DTALite_PATH, 'DTALite.exe'), time_period_path)
        for f in os.listdir(DTA_BASE_PATH):
            copy(os.path.join(DTA_BASE_PATH, f), time_period_path)
        batch_lines.append('cd {0}\TimePeriods\{1}'.format(BASE_PATH, period))
        batch_lines.append('DTALite.exe')

batch_lines.append('cd {}\DemandModel'.format(BASE_PATH))
batch_lines.append('python 5_spectral_post_processing.py')
batch_lines.append('python 6_cleanup.py')

#batch_lines = ['cd D:\ShoresideTDM\TimePeriods\AM', 'DTALite.exe', 'Pause']

f = open(BATCH_FILE, 'w')
f.write('\n'.join(batch_lines))
f.close()

#call('D:\ShoresideTDM\TimePeriods\AM\DTALite.exe', shell = True)

#call(BATCH_FILE, shell = True)
#os.remove(BATCH_FILE)

#Cleaning Up
#for period in time_periods.index:
#    time_period_path = os.path.join(BASE_PATH, r'TimePeriods\{}'.format(period))
#    for f in os.listdir(time_period_path):
#        os.remove(os.path.join(time_period_path, f))
#    os.rmdir(time_period_path)

print('Done')

#os.system('python ' + os.path.join(DEMAND_MODEL_PATH, 'generation.py'))
#os.system('python ' + os.path.join(DEMAND_MODEL_PATH, 'distribution.py'))