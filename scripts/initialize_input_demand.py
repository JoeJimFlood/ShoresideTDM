import pandas as pd
import numpy as np

nodes_file = r'D:\ShoresideTDM\TimePeriods\AM\input_node.csv'
input_demand_file = nodes_file.replace('input_node', 'input_demand')

nodes = pd.read_csv(nodes_file)
node_list = list(nodes['node_id'])
N = len(node_list)

demand = pd.melt(pd.DataFrame(np.zeros((N, N)), node_list, node_list))
demand['from_zone_id'] = demand['variable']
demand['to_zone_id'] = N*node_list
demand['variable'] = demand['value']

demand.set_index('from_zone_id')[['to_zone_id', 'variable']].to_csv(input_demand_file)