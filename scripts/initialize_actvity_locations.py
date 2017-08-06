import pandas as pd
import numpy as np

demand_source_file = r'D:\ShoresideTDM\Network\node_info.csv'
activity_location_file = r'D:\ShoresideTDM\TimePeriods\AM\input_activity_location.csv'

type_external_map = {1: 0,
                     2: 0,
                     3: 0,
                     4: 1}

node_info = pd.read_csv(demand_source_file)
activity = node_info[node_info['Area'] > 0]
activity['External'] = activity['Type'].map(type_external_map)
activity['Zone'] = range(1, len(activity.index)+1)

activity_location = pd.DataFrame(np.zeros_like(activity[['Node', 'External', 'Zone']]),
                                 index = activity.index,
                                 columns = ['zone_id', 'node_id', 'external_OD_flag'])
for node in activity.index:
    activity_location.loc[node] = list(activity[['Zone', 'Node', 'External']].loc[node])

activity_location.set_index('zone_id').to_csv(activity_location_file)