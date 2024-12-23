import sys
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

if __name__ == "__main__":
    if len(sys.argv)!=15:
        print("Error - usage:\n >>> python3 Plot_distribution.py [In.txt] [delimiter] [col-index(0-indexed)] [0/1:Headers] [min-x] [max-x(-1 for no max)] [min-y] [max-y] [title] [x-lbl] [y-lbl] [0/1:X-log] [0/1:Y-log] [Out.png]\n")
        exit()
        
    in_fname, delim, ind, headers, min_x, max_x, min_y, max_y, title, xlbl, ylbl, xlog, ylog, out_fname = sys.argv[1:]
    ind, min_x, max_x, min_y, max_y = [int(ele) for ele in [ind, min_x, max_x, min_y, max_y]]
    
    title = title.replace("FMT","CMT")  # bandaid
    
    # Auto-detect delimiter based on file extension
    ext = in_fname.split(".")[-1]
    if ext == 'csv':
        delim = ','
    elif ext == 'tsv':
        delim = '\t'
    
    # Read the data
    In = open(in_fname)
    if headers == "1":
        Header = In.readline()[:-1].split(delim)[ind]
    vals = []
    line = In.readline()
    while line != "":
        temp = line[:-1].split(delim)
        if len(temp)>ind:
            v = float(temp[ind])
            vals.append(v)
        line = In.readline()
    In.close()
    
    if headers == "1":
        plt.title(Header)
    
    # Set x-axis limits
    if min_x == -1:
        min_x = min(vals)
    if max_x == -1:
        max_x = max(vals)
    
    # Create the histogram first to get the count data
    if xlog == '1':
        if min_x <= 0:
            min_x = min(filter(lambda x: x > 0, vals), default=0.1)
        logbins = np.logspace(np.log10(min_x), np.log10(max_x), 26)  # 25 bins = 26 edges
        counts, bins, _ = plt.hist(vals, bins=logbins, edgecolor='black', linewidth=1.2)
    else:
        bins = np.linspace(min_x, max_x, 26)  # 25 bins = 26 edges
        counts, bins, _ = plt.hist(vals, bins=bins, edgecolor='black', linewidth=1.2)
    
    # Clear the current histogram since we just used it to get the counts
    plt.clf()
    
    # Now plot again with proper y-limits
    if xlog == '1':
        plt.hist(vals, bins=logbins, edgecolor='black', linewidth=1.2)
    else:
        plt.hist(vals, bins=bins, edgecolor='black', linewidth=1.2)
    
    # Set axis scales
    if xlog == '1':
        plt.xscale('log')
    if ylog == '1':
        plt.yscale('log')
    
    # Set y-axis limits
    if min_y == -1:
        min_y = 0
    if max_y == -1:
        max_y = max(counts) * 1.1  # Add 10% padding above maximum count
    
    print(f"Plotting from: {min_x} to {max_x} (x-axis), and {min_y} to {max_y} (y-axis)")
    
    plt.ylim(min_y, max_y)
    plt.xlim(min_x, max_x)
    
    # Set labels and title
    plt.xlabel(xlbl, fontweight='bold', fontsize=20)
    plt.ylabel(ylbl, fontweight='bold', fontsize=20)
    plt.title(title, fontweight='bold', fontsize=20)
    
    # Style the axis labels
    ax = plt.gca()
    for label in ax.get_yticklabels():
        label.set_fontweight('bold')
    for label in ax.get_xticklabels():
        label.set_fontweight('bold')
    
    # Add thousands separator to y-axis if not in log scale
    def thousands(x, pos):
        return f'{int(x):,}'
    if ylog == '0':
        formatter = FuncFormatter(thousands)
        ax.yaxis.set_major_formatter(formatter)
    
    plt.tight_layout()
    plt.savefig(out_fname)
