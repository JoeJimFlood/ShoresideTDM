import os
import time
import datetime
from subprocess import call

start_time = datetime.datetime.now()

BASE_PATH = os.path.split(__file__)[0]
TIME_LOG = os.path.join(BASE_PATH, 'TimeLog.txt')
MODEL_BATCH = os.path.join(BASE_PATH, 'RunModel.bat')

lines = [r'==/|\===Shoreside CBD TDM Run Start: {}===/|\=='.format(start_time.strftime('%d.%m.%y.%H.%M.%S'))]
lines.append(len(lines[0])*'-')
lines.append(' ')

logfile = open(TIME_LOG, 'w')
logfile.write('\n'.join(lines))
logfile.close()

call(MODEL_BATCH)