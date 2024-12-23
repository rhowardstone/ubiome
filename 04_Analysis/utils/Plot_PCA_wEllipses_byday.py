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

# UNTR_d0_GR_M_a1
#ABX10_d0_GR_F

#blue_star = mlines.Line2D([], [], color='blue', marker='*', linestyle='None',
#                          markersize=10, label='Blue stars')

if __name__ == "__main__":
	if len(sys.argv)!=11:
		print("Error - usage:\n >>> python3 Plot_PCA_wEllipses_byday.py [PCA.tsv] [PCA-ratvars.txt] [permanova-file.csv] [day1,day2,...] [0/1 draw ellipses?] [XMIN] [XMAX] [YMIN] [YMAX] [Out_basename]\n")
		print("Title will be taken as written for full plot, each day will have 'Title: day#' added")
		exit()
	in_fname, rats_fname, perm_fname, days_to_plot, make_ellipse, XMIN, XMAX, YMIN, YMAX, out_fname = sys.argv[1:]
	XMIN, XMAX, YMIN, YMAX = [float(ele) for ele in (XMIN, XMAX, YMIN, YMAX)]
	days_to_plot = set(days_to_plot.split(","))
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
	#Read in perMANOVA file (perm_results['UNTR']['d0'] gives the row for just those as:	
	#Pval	eta-sqr	F	A	B	Pval	bonf	eta-sqr	F	t
	
	Colors = {'LJ':'#F9564F', 'GR':'#3ABECF'}
	custom_labels = []
	for col in Colors:
		temp = mlines.Line2D([], [], color=Colors[col], marker='o',linestyle='None', markersize=8, label=col) #markersize=loc_sizes_legend[loc]
		custom_labels.append(temp)	
		
	Points = {}   #Points['UNTR']['d0']['LJ'][0] = [(x1,y1), (x2, ...]
	
	In = open(in_fname)
	line = In.readline()
	while line != "":
		lbl, x, y = line[:-1].split("\t")[:3]   #UNTR_d0_GR_M_a1

		if lbl.find('_')!=-1: #discard wildtype samples for now
			group, day, site, gender, animal = lbl.split("_")  #will throw an error if using pooled samples
			
			if group in Points:
				if day in Points[group]:
					if site in Points[group][day]:
						Points[group][day][site].append([float(x), float(y)])
					else:
						Points[group][day][site] = [[float(x), float(y)]]
				else:
					Points[group][day] = {site: [[float(x), float(y)]]}
			else:
				Points[group] = {day: {site: [[float(x), float(y)]]}}
		
		line = In.readline()  # ^^ still gross but maybe less and more useful
	In.close()
	
	
	for group in Points:
		for day in Points[group]:
			if day in days_to_plot:
				#9.6,7.2
				fig, ax = plt.subplots(1,1,figsize=(6.4*1.5,4.8*1.5))  #why this size ..? well, can we do better than hardcoding this gross thing?
				
				for s in Colors:
					for i in range(len(Points[group][day][s])):
						ax.scatter(Points[group][day][s][i][0], Points[group][day][s][i][1], c=Colors[s], alpha=0.6, s=72) #, size=4)
				
				
				#ax.set_xlabel(xlbl, fontsize=20)
				#ax.set_ylabel(ylbl, fontsize=20)
				#ax.tick_params(axis='x', labelsize=24)
				#ax.tick_params(axis='y', labelsize=24)
				#ax = plt.gca()
				# Set y-axis tick labels to bold?
				ax.set_xlabel(xlbl, fontsize=32, fontweight='bold')
				ax.set_ylabel(ylbl, fontsize=32, fontweight='bold')
				## These two were commented out .. does this mess up anything else?
				
				
				ax.tick_params(axis='x', labelsize=30)
				ax.tick_params(axis='y', labelsize=30)
				for label in ax.get_yticklabels():
					label.set_fontweight('bold')
				for label in ax.get_xticklabels():
					label.set_fontweight('bold')
		
				
				if make_ellipse == '1':
					confidence_ellipse(np.array(Points[group][day]['LJ']), ax, edgecolor='#F9564F')
					confidence_ellipse(np.array(Points[group][day]['GR']), ax, edgecolor='#3ABECF')
				
				r_squared_value = 100 * float(perm_results[group][day][1])  #calculate this here (this was included)
				p_value = float(perm_results[group][day][0])
				
				#ax.add_artist(AnchoredText(r"$R^2 = {}$\\n$p = {}$%".format(r_squared_value, p_value), loc=1, prop={'size': 24}))
				#ax.add_artist(AnchoredText(r"$R^2 = {:.1f}\% \\n p = {:.2g}$".format(r_squared_value, p_value), loc=1, prop={'size': 24}))
				
				#formatted_string = r"$R^2 = {:.1f}\%, \ p = {:.4f}$".format(r_squared_value, p_value)
				#ax.add_artist(AnchoredText(formatted_string, loc=1, prop={'size': 32, 'fontweight':'bold'}))
				
				significance = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""
				formatted_string = "η² = {:.1f}% ({})".format(r_squared_value, significance)  #permANOVA values here
				ax.add_artist(AnchoredText(formatted_string, loc=1, prop={'size': 32, 'fontweight': "bold"}))
				ax.xaxis.set_major_locator(ticker.MaxNLocator(5))  # Approx. 5 x-ticks
				ax.yaxis.set_major_locator(ticker.MaxNLocator(5))  # Approx. 4 y-ticks
				
				plt.title(f'{group}', fontweight='bold', fontsize=32)
				artist = ax.add_artist(AnchoredText("Day "+day[1:], loc='lower left', prop={'size': 32, 'fontweight':'bold'}))
				
				artist.set_alpha(0.7)
				
				plt.xlim([XMIN,XMAX])
				plt.ylim([YMIN,YMAX])
				
				fig.tight_layout()
				plt.savefig(out_fname+"_"+group+"_"+day+".png")
				
				plt.clf()
				plt.close()
	
	#Points['All']['d0']['LJ'] = #Points['UNTR']['d0']['LJ'] = [(x1,y1), (x2, ...]
	
