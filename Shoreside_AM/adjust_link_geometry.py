from __future__ import division
import pandas as pd
import numpy as np
from math import pi
import os
from subprocess import Popen

wd = os.getcwd()
fp = os.path.join(wd, 'input_link.csv')
data = pd.DataFrame.from_csv(fp, index_col = None)

adj = 0.002841
outdata = pd.DataFrame(columns = data.columns)

def adjust_links(from_node_id, to_node_id):
    global data, adj, outdata
    
    link = data[data['from_node_id'] == from_node_id]
    link = link[link['to_node_id'] == to_node_id]
    geo = link['geometry'].iloc[0]
    coords = geo[25:-27]
    (from_coord, to_coord) = coords.split(' ')
    x1, y1, z1 = from_coord.split(',')
    x2, y2, z2 = to_coord.split(',')

    x1 = float(x1)
    x2 = float(x2)
    y1 = float(y1)
    y2 = float(y2)

    heading = np.angle((x2 - x1) + 1j*(y2 - y1))
    right = heading - pi/2
    adjustment_vector = adj*np.exp(1j*right)

    x1 += np.real(adjustment_vector)
    x2 += np.real(adjustment_vector)
    y1 += np.imag(adjustment_vector)
    y2 += np.imag(adjustment_vector)

    x1 = str(round(x1, 6))
    x2 = str(round(x2, 6))
    y1 = str(round(y1, 6))
    y2 = str(round(y2, 6))

    new_start = ','.join([x1, y1, z1])
    new_end = ','.join([x2, y2, z2])
    new_coords = ' '.join([new_start, new_end])
    new_geo = '<LineString><coordinates>{}</coordinates></LineString>'.format(new_coords)

    link['geometry'] = new_geo

    if len(outdata.index) == 0:
        outdata.loc[0] = link.values[0]

    else:
        i = max(outdata.index)
        outdata.loc[i+1] = link.values[0]

#adjust_link(61, 83)
#adjust_link(83, 61)
adjust_links(83, 84)
adjust_links(84, 83)
adjust_links(84, 85)
adjust_links(85, 84)
adjust_links(86, 102)
adjust_links(102, 86)
adjust_links(104, 103)
adjust_links(103, 104)
adjust_links(103, 101)
adjust_links(101, 103)
adjust_links(101, 99)
adjust_links(99, 101)
adjust_links(99, 96)
adjust_links(96, 99)
adjust_links(96, 91)
adjust_links(91, 96)
adjust_links(91, 90)
adjust_links(90, 91)
adjust_links(90, 93)
adjust_links(93, 90)
adjust_links(82, 89)
adjust_links(89, 82)
adjust_links(89, 92)
adjust_links(92, 89)
adjust_links(82, 91)
adjust_links(91, 82)
adjust_links(91, 89)
adjust_links(89, 91)
adjust_links(89, 90)
adjust_links(90, 89)
adjust_links(90, 82)
adjust_links(82, 90)
adjust_links(101, 102)
adjust_links(102, 101)
adjust_links(103, 102)
adjust_links(102, 103)
adjust_links(86, 85)
adjust_links(85, 86)
adjust_links(86, 84)
adjust_links(84, 86)
adjust_links(85, 87)
adjust_links(87, 85)
adjust_links(87, 93)
adjust_links(93, 87)
adjust_links(93, 95)
adjust_links(95, 93)
adjust_links(100, 97)
adjust_links(97, 100)
adjust_links(97, 98)
adjust_links(98, 97)
adjust_links(98, 87)
adjust_links(87, 98)

outfile = os.path.join(wd, 'LinkAdjustOut.csv')
outdata.to_csv(outfile)
Popen(outfile, shell = True)