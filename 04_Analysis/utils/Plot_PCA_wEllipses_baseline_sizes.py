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
	
### THIS SCRIPT WAS NEVER FINISHED -- REDO SIMPLER, THIS IS GROSS ###
### THIS SCRIPT WAS NEVER FINISHED -- REDO SIMPLER, THIS IS GROSS ###
### THIS SCRIPT WAS NEVER FINISHED -- REDO SIMPLER, THIS IS GROSS ###
### THIS SCRIPT WAS NEVER FINISHED -- REDO SIMPLER, THIS IS GROSS ###
### THIS SCRIPT WAS NEVER FINISHED -- REDO SIMPLER, THIS IS GROSS ###

# UNTR_d0_GR_M_a1
#ABX10_d0_GR_F

#blue_star = mlines.Line2D([], [], color='blue', marker='*', linestyle='None',
#                          markersize=10, label='Blue stars')

if __name__ == "__main__":
	if len(sys.argv)!=13:
		print("Error - usage:\n >>> python3 Plot_PCA_wEllipses_baseline.py [PCA.tsv] [PCA-ratvars.txt] [permanova-file.csv] [x-lbl] [y-lbl] [Title] [0/1 ellipse?] [x-min] [x-max] [y-min] [y-max] [Out_basename]\n")
		print("Title will be taken as written for full plot, each day will have 'Title: day#' added")
		exit()
	in_fname, rats_fname, perm_fname, xlbl, ylbl, title, to_ellipse, XMIN, XMAX, YMIN, MAX,3out_fname = sys.argv[1:]
	
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
	#Read in perMANOVA file (perm_results['UNTR']['0'] gives the row for just those as:	
	#Pval	eta-sqr	F	A	B	Pval	bonf	eta-sqr	F	t
	
	print()
	print(in_fname)
	print(sorted(perm_results))
	print(sorted(perm_results['-1']))
	print()
	r_squared_value = 100 * float(perm_results['-1']['d-2'][1])
	p_value = float(perm_results['-1']['d0'][0]) #LOAD THEM HERE
	
	Colors = {'LJ':'#F9564F', 'GR':'#3ABECF'}
	Shapes = {g:'o' for g in 'UNTR ABX3FMT ABX10 FMT'.split()}
	Sizes = {'GR':24, 'LJ':24}
	
	wild_size = 24
	wild_color = '#0F0A0D'
	wild_shape = '.'
		
	Sizes_legend = {'GR':5, 'LJ':10}
	
	custom_labels = []
	for col in Colors:
		temp = mlines.Line2D([], [], color=Colors[col], marker='o',linestyle='None', markersize=8, label=col) #markersize=loc_sizes_legend[loc]
		custom_labels.append(temp)
	LJ_points, GR_points = [], []
	
	day_indices, i = {'d60':[], 'd30':[], 'd10':[], 'd8':[], 'd5':[], 'd3':[], 'd1':[], 'd0':[]}, 0
	X, Y, shapes, sizes, colors, names, days = [], [], [], [], [], [], []
	In = open(in_fname)
	line = In.readline()
	while line != "":
		lbl, x, y = line[:-1].split("\t")[:3]   #UNTR_d0_GR_M_a1
		lbl = lbl.split("_")
		
		if len(lbl)==1:
			size, color, shape = wild_size, wild_color, wild_shape
			days.append('W')
			for d in day_indices:
				day_indices[d].append(i)
		else:
			size = 72 #Sizes[lbl[2]]  #loc
			color = Colors[lbl[2]] #loc
			shape = Shapes[lbl[0]] #grp
			day_indices[lbl[1]].append(i)
			days.append(lbl[1])
			if lbl[1] == 'd0':
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
	
	fig, ax = plt.subplots(1,1,figsize=(6.4*1.5,4.8*1.5))
	for i in range(len(X)):
		if days[i] == 'd0':
			ax.scatter(X[i], Y[i], label=names[i], s=sizes[i], c=colors[i], marker=shapes[i], alpha=0.6) #, size=4)
	
	#ax.legend(handles=custom_labels, loc='center left', bbox_to_anchor=(1,0.5), fontsize=8)
	#ax.set_title(title, fontsize=24)
	
	LJ_points = np.array(LJ_points)
	GR_points = np.array(GR_points)
	
	if to_ellipse == '1':
		confidence_ellipse(LJ_points, ax, edgecolor='#F9564F')
		confidence_ellipse(GR_points, ax, edgecolor='#3ABECF')
		plt.xlim([-0.62, 0.68])
		plt.ylim([-0.55, 0.6])
		ax.add_artist(AnchoredText("Day 0", loc='lower left', prop={'size': 32, 'fontweight':'bold'}))
		ax.xaxis.set_major_locator(ticker.MaxNLocator(5))  # Approx. 5 x-ticks
		ax.yaxis.set_major_locator(ticker.MaxNLocator(5))  # Approx. 4 y-ticks
		plt.title(f'Baseline (all groups)', fontweight='bold', fontsize=32)
	else:
		#bandaid:
		level = rats_fname.split("_")[2]
		ylims = ax.get_ylim()
		if level == 'genus':
			plt.ylim([ylims[0], ylims[1]+0.2])
		elif level != 'V3V4':
			plt.ylim([ylims[0], ylims[1]+0.12])
		else:
			plt.ylim([ylims[0], ylims[1]+0.08])
		ax.xaxis.set_major_locator(ticker.MaxNLocator(4))
		ax.set_xlabel(xlbl, fontsize=32, fontweight='bold')
		ax.set_ylabel(ylbl, fontsize=32, fontweight='bold')
	ax.tick_params(axis='x', labelsize=30)
	ax.tick_params(axis='y', labelsize=30)
	for label in ax.get_yticklabels():
		label.set_fontweight('bold')
	for label in ax.get_xticklabels():
		label.set_fontweight('bold')
	
	
	
	
	#ax.add_artist(AnchoredText(r"$R^2 = {}%$\n$p = {}$%".format(r_squared_value, p_value), loc=1, prop={'size': 24}))
	#formatted_string = r"$R^2 = {:.1f}\%, \ p = {:.4f}$".format(r_squared_value, p_value)
	#ax.add_artist(AnchoredText('would this be bold', loc=1, prop={'size': 32, 'fontweight':"bold"}))
	
	
	
	significance = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""
	formatted_string = "η² = {:.1f}% ({})".format(r_squared_value, significance)
	ax.add_artist(AnchoredText(formatted_string, loc=1, prop={'size': 32, 'fontweight': "bold"})) #PERMANOVA VALUES HERE
	
	#artist.set_alpha(0.7)

	#plt.xlim([-0.62, 0.68])
	#plt.ylim([-0.55, 0.61])
	plt.xlim([-1, 1]) 
	plt.ylim([-1, 1])
	fig.tight_layout()
	plt.savefig(out_fname+"_baseline_check.png")
	
	
	
	
