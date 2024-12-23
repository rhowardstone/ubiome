import sys
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
from matplotlib import patches
import pandas as pd
from math import dist
from Get_ellipses3 import confidence_ellipse
from matplotlib.offsetbox import AnchoredText
import matplotlib.ticker as ticker

if __name__ == "__main__":
    if len(sys.argv)!=13:
        print("Error - usage:\n >>> python3 Plot_PCA_wEllipses_baseline.py [PCA.tsv] [PCA-ratvars.txt] [permanova-file.csv] [x-lbl] [y-lbl] [Title] [0/1 ellipse?] [XMIN (-1 for padded min)] [XMAX] [YMIN] [YMAX] [Out_basename]\n")
        print("Title will be taken as written for full plot, each day will have 'Title: day#' added")
        exit()
    in_fname, rats_fname, perm_fname, xlbl, ylbl, title, to_ellipse, XMIN, XMAX, YMIN, YMAX, out_fname = sys.argv[1:]
    XMIN, XMAX, YMIN, YMAX = [float(ele) for ele in (XMIN, XMAX, YMIN, YMAX)]
    
    In = open(rats_fname)
    xlbl = "Axis1 ["+str(round(100*float(In.readline()),2))+"%]"
    ylbl = "Axis2 ["+str(round(100*float(In.readline()),2))+"%]"
    In.close()
    
    perm_results, In = {}, open(perm_fname)
    line = In.readline()
    line = In.readline()
    while line != "":
        temp = line[:-1].split("\t")
        if len(temp)>1:
            day, group = temp[:2]
            if group in perm_results:
                perm_results[group][day] = temp[2:]
            else:
                perm_results[group] = {day:temp[2:]}    
        line = In.readline()
    In.close()
    
    print()
    print(in_fname)
    #print(sorted(perm_results))
    #print(sorted(perm_results['-1']))
    #print()
    r_squared_value = 100 * float(perm_results['-1']['d-2'][1])
    p_value = float(perm_results['-1']['d-2'][0])
    
    Colors = {'LJ':'#F9564F', 'GR':'#3ABECF'}
    Shapes = {g:'o' for g in 'UNTR ABX3CMT ABX10 CMT'.split()}
    Sizes = {'GR':24, 'LJ':24}
    
    wild_size = 24
    wild_color = '#0F0A0D'
    wild_shape = '.'
        
    Sizes_legend = {'GR':5, 'LJ':10}
    
    custom_labels = []
    for col in Colors:
        temp = mlines.Line2D([], [], color=Colors[col], marker='o',linestyle='None', markersize=8, label=col)
        custom_labels.append(temp)
    LJ_points, GR_points = [], []
    
    day_indices, i = {'d60':[], 'd30':[], 'd10':[], 'd8':[], 'd5':[], 'd3':[], 'd1':[], 'd-2':[]}, 0
    X, Y, shapes, sizes, colors, names, days = [], [], [], [], [], [], []
    In = open(in_fname)
    line = In.readline()
    while line != "":
        lbl, x, y = line[:-1].split("\t")[:3]
        lbl = lbl.split("_")
        
        if len(lbl)==1:
            size, color, shape = wild_size, wild_color, wild_shape
            days.append('W')
            for d in day_indices:
                day_indices[d].append(i)
        else:
            size = 72
            color = Colors[lbl[2]]
            shape = Shapes[lbl[0]]
            day_indices[lbl[1]].append(i)
            days.append(lbl[1])
            if lbl[1] == 'd-2':
                if lbl[2] == 'LJ':
                    LJ_points.append([float(x), float(y)])
                else:
                    GR_points.append([float(x), float(y)])
        i+=1
        
        X.append(float(x))
        Y.append(float(y))
        sizes.append(size)
        colors.append(color)
        shapes.append(shape)
        names.append("_".join(lbl[:-2]))
        
        line = In.readline()
    In.close()

    # Calculate limits if not specified
    if XMIN == -1:
        XMIN = min(X)
    if XMAX == -1:
        XMAX = max(X)
    if YMIN == -1:
        YMIN = min(Y)
    if YMAX == -1:
        YMAX = max(Y)
    
    # Add vertical buffer
    y_range = YMAX - YMIN
    y_buffer = y_range / 16
    YMAX = YMAX + y_buffer
    YMIN = YMIN - y_buffer
    
    x_range = XMAX - XMIN
    x_buffer = x_range / 16
    XMAX = XMAX + x_buffer
    XMIN = XMIN - x_buffer
    
    fig, ax = plt.subplots(1,1,figsize=(6.4*1.5,4.8*1.5))
    for i in range(len(X)):
        if days[i] == 'd-2':
            ax.scatter(X[i], Y[i], label=names[i], s=sizes[i], c=colors[i], marker=shapes[i], alpha=0.6)
    
    LJ_points = np.array(LJ_points)
    GR_points = np.array(GR_points)
    
    if to_ellipse == '1':
        confidence_ellipse(LJ_points, ax, edgecolor='#F9564F')
        confidence_ellipse(GR_points, ax, edgecolor='#3ABECF')
        ax.add_artist(AnchoredText("Day -2", loc='lower left', prop={'size': 32, 'fontweight':'bold'}))
        ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
        ax.yaxis.set_major_locator(ticker.MaxNLocator(5))
        plt.title(f'Baseline (all groups)', fontweight='bold', fontsize=32)
    else:
        ax.xaxis.set_major_locator(ticker.MaxNLocator(4))
    
    ax.set_xlabel(xlbl, fontsize=32, fontweight='bold')
    ax.set_ylabel(ylbl, fontsize=32, fontweight='bold')
    ax.tick_params(axis='x', labelsize=30)
    ax.tick_params(axis='y', labelsize=30)
    
    for label in ax.get_yticklabels():
        label.set_fontweight('bold')
    for label in ax.get_xticklabels():
        label.set_fontweight('bold')
    
    significance = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""
    formatted_string = "η² = {:.1f}% ({})".format(r_squared_value, significance)
    artist = ax.add_artist(AnchoredText(formatted_string, loc=1, prop={'size': 32, 'fontweight': "bold"}))
    
    artist.set_alpha(0.7)

    plt.xlim([XMIN, XMAX])
    plt.ylim([YMIN, YMAX])
    
    fig.tight_layout()
    plt.savefig(out_fname+"_baseline_check.png")
