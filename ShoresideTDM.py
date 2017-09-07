

#Popen(BATCH_FILE, shell = True)
#command = 'cmd c/ {}'.format(BATCH_FILE)
#os.system(command)

#p = Popen(BATCH_FILE, cwd = BASE_PATH)
#stdout, stderr = p.communicate()

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