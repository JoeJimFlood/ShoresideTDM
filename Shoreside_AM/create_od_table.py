import pandas as pd
import os

wd = os.getcwd()
infile = os.path.join(wd, 'Zone Summary.xlsx')
depfile = os.path.join(wd, 'OD_Dep.csv')
retfile = os.path.join(wd, 'OD_Ret.csv')
data = pd.read_excel(infile, 'Disaggregate Demand')

dep = data[data['Direction'] == 'Depart']
ret = data[data['Direction'] == 'Return']

dep['O'] = dep['Origin']
dep['D'] = dep['Destination']
ret['O'] = ret['Destination']
ret['D'] = ret['Origin']

times = data.columns[5:].tolist()

dep_by_od = dep[['O', 'D'] + times].groupby(['O', 'D']).sum()
ret_by_od = ret[['O', 'D'] + times].groupby(['O', 'D']).sum()

dep_by_od.to_csv(depfile)
ret_by_od.to_csv(retfile)

print 'Go'