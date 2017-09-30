'''
Utility functions
'''
from __future__ import division
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def pack(dists, K, dtype = np.float16):
    '''
    Packs profiles into a Pandas Data Frame containing the Fourier coefficients of the log-flow

    Parameters
    ----------
    dists (dict):
        Dictionary with the link ID as the keys and spectral.profiles as the values
    K (int):
        Maximum number of Fourier coefficients to save
    dtype (data type):
        Data type to store all values

    Returns
    -------
    outdata (pandas.DataFrame):
        Data frame containing the Fourier coefficients of the log-flow for each profile in `dists`
    '''
    N = len(dists)

    #Define columns of output
    outdata_columns = ['L0']
    for k in range(1, K+1):
        outdata_columns += ['L%dre'%(k), 'L%dim'%(k)]

    outdata = pd.DataFrame(np.zeros((N, 2*K+1), dtype), index = dists.keys(), columns = outdata_columns)

    #For each link in dists, extract the id and Fourier coefficients of the log-pdf
    for link_id in dists.keys():
        outdata.loc[link_id, 'L0'] = dtype(np.real(dists[link_id].L.c[0]) + np.log(dists[link_id].total))
        for k in range(1, K+1):
            try:
                Lk = dists[link_id].L.c[k]
            except IndexError: #If the profile has more Fourier coefficients than the specified number to save, assume the next one is zero (it really is anyway)
                Lk = 0
            outdata.loc[link_id, 'L%dre'%(k)] = dtype(np.real(Lk))
            outdata.loc[link_id, 'L%dim'%(k)] = dtype(np.imag(Lk))

    outdata.index.name = 'LinkID'
    return outdata

def plot_link(dists, data, link_id, title, font_size, font, fp = None):
    '''
    Plots a profile with a bar graph it was based on. Saves it if a filepath is specified, otherwise it is simply shown

    Parameters
    ----------
    dists (dict):
        Dictionary with the link ID as the keys and spectral.profiles as the values
    data (pandas.DataFrame):
        Data Frame containing volumes over various time periods for each link in `dists`.
    link_id (int):
        ID of link to plot
    title (str):
        Plot title
    font_size (int):
        Font size for text
    font (str):
        Font to use in plots
    fp (str, optional):
        Filepath to save plot
    '''
    plt.figure(figsize = (16, 9))
    link_data = data.loc[link_id]

    #Define paramters for bar chart of pre-spectral data
    locs = np.array(link_data.index)
    widths = np.diff(np.append(locs, 24))
    heights = np.array(link_data) / widths

    #Plot vertical bars every three hours
    ymax = 1.25*(heights.max())
    for i in range(0, 25, 3):
        plt.plot([i, i], [0, ymax], color = 'k')

    #Plot everything
    plt.bar(locs, heights, widths, color = '#c0c0c0', edgecolor = 'k', align = 'edge')
    dists[link_id].plot(1440, pdf = False, linewidth = 3, color = '#0000ff')

    xticks = list(range(25))
    xlabels = ['12 AM', '', '', '3 AM', '', '', '6 AM', '', '', '9 AM', '', '',
               '12 PM', '', '', '3 PM', '', '', '6 PM', '', '', '9 PM', '', '',
               '12 AM']

    plt.xlim(0, 24)
    plt.ylim(0, ymax)
    plt.xticks(xticks, xlabels, fontsize = font_size, fontname = font, rotation = 5)
    plt.ylabel('Flow (Vehicles per Hour)', fontsize = font_size, fontname = font)
    plt.yticks(fontsize = font_size, fontname = font)
    plt.title(title, fontsize = font_size, fontname = font, va = 'bottom')
    plt.grid(True)

    if fp:
        plt.savefig(fp)
        plt.clf()
    else:
        plt.show()

def plot_links(dists, link_ids, links_of_interest, ymax, title, font_size, font, fp = None):
    '''
    Plots selected links with the selected titles. Saves plot if a filepath is specified

    Parameters
    ----------
    dists (dict):
        Dictionary with the link ID as the keys and spectral.profiles as the values

    '''
    plt.figure(figsize = (16, 9))

    for i in range(0, 25, 3):
        plt.plot([i, i], [0, ymax], color = 'k')
    
    for link_id in link_ids:
        dists[link_id].plot(1440, pdf = False, linewidth = 3,
                            color = links_of_interest[link_id][1],
                            linestyle = links_of_interest[link_id][2],
                            label = links_of_interest[link_id][0])

    xticks = list(range(25))
    xlabels = ['12 AM', '', '', '3 AM', '', '', '6 AM', '', '', '9 AM', '', '',
               '12 PM', '', '', '3 PM', '', '', '6 PM', '', '', '9 PM', '', '',
               '12 AM']

    plt.xlim(0, 24)
    plt.ylim(0, ymax)
    plt.xticks(xticks, xlabels, fontsize = font_size, fontname = font, rotation = 5)
    plt.ylabel('Flow (Vehicles per Hour)', fontsize = font_size, fontname = font)
    plt.yticks(fontsize = font_size, fontname = font)

    plt.grid(True)
    plt.title(title, fontsize = font_size, fontname = font, va = 'bottom')
    
    legend = plt.legend(loc = 'upper left')
    for text in legend.get_texts():
        text.set_fontname(font)
        text.set_size(font_size)
    
    if fp:
        plt.savefig(fp)
        plt.clf()
    else:
        plt.show()