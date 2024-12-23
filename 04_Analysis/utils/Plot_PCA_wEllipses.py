import sys
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
from Get_ellipses3 import confidence_ellipse # as confidence_ellipse2
from Get_ellipses import confidence_ellipse as confidence_ellipse1
from matplotlib.offsetbox import AnchoredText
from matplotlib import patches
import pandas as pd

'''
    print("Ellipse has the parametric equation:")
    print("x(t) = a*cos(t)*cos(theta) - b*sin(t)*sin(theta) + cx")
    print("y(t) = a*cos(t)*sin(theta) + b*sin(t)*cos(theta) + cy")
    print("with:")
    print(f"a = {eq.semimajor}")
    print(f"b = {eq.semiminor}")
    print(f"cx = {eq.cx}")
    print(f"cy = {eq.cy}")
    print(f"theta = {eq.theta}")
'''

# UNTR_d0_GR_M_a1
#ABX10_d0_GR_F

#blue_star = mlines.Line2D([], [], color='blue', marker='*', linestyle='None',
#                          markersize=10, label='Blue stars')

if __name__ == "__main__":
	if len(sys.argv)!=6:
		print("Error - usage:\n >>> python3 Plot_PCA.py [PCA.tsv] [x-lbl] [y-lbl] [Title] [Out_basename]\n")
		print("Title will be taken as written for full plot, each day will have 'Title: day#' added")
		exit()
	in_fname, xlbl, ylbl, title, out_fname = sys.argv[1:]
	
	#day_sizes = {'d60':38, 'd30':33, 'd10':28, 'd8':23, 'd5':18, 'd3':13, 'd1':8, 'd0':3}
	#Colors = {'UNTR':'#4363D8', 'ABX3FMT':'#3CB44B', 'ABX10':'#E6194B', 'FMT':'#42D4F4'}
	#Shapes = {'GR':'o', 'LJ':'x'}
	Colors = {'LJ':'#F9564F', 'GR':'#3ABECF'}
	Shapes = {g:'o' for g in 'UNTR ABX3CMT ABX10 CMT'.split()}
	
	#Colors = {'d60':'#000000', 'd30':'#9400D3', 'd10':'#4B0082', 'd8':'#0000FF', 'd5':'#00FF00', 'd3':'#FFFF00', 'd1':'#FF7F00', 'd0':'#FF0000'}
	
	#Shapes = {'UNTR':'o', 'ABX3FMT':'x', 'ABX10':'^', 'FMT':'s'}
	Sizes = {'GR':24, 'LJ':24}
	
	wild_size = 24
	wild_color = '#0F0A0D'
	wild_shape = '.'
	
	Sizes_legend = {'GR':5, 'LJ':10}
	
	custom_labels = []
	for col in Colors:
		temp = mlines.Line2D([], [], color=Colors[col], marker='o',linestyle='None', markersize=8, label=col) #markersize=loc_sizes_legend[loc]
		custom_labels.append(temp)
		
	custom_labels.append(mlines.Line2D([], [], color=wild_color, marker=wild_shape,linestyle='None', markersize=8, label='Wildtype')) #markersize=loc_sizes_legend[loc]
	
	LJ_points, GR_points = [], []
	
	day_indices, i = {'d60':[], 'd30':[], 'd10':[], 'd8':[], 'd5':[], 'd3':[], 'd1':[], 'd-2':[]}, 0
	X, Y, shapes, sizes, colors, names = [], [], [], [], [], []
	In = open(in_fname)
	line = In.readline()
	while line != "":
		lbl, x, y = line[:-1].split("\t")[:3]   #UNTR_d0_GR_M_a1
		lbl = lbl.split("_")
		if len(lbl)==1:
			size, color, shape = wild_size, wild_color, wild_shape
			for d in day_indices:
				day_indices[d].append(i)
		else:
			size = 36 #Sizes[lbl[2]]  #loc
			color = Colors[lbl[2]] #loc
			shape = Shapes[lbl[0]] #grp
			day_indices[lbl[1]].append(i)
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
		ax.scatter(X[i], Y[i], label=names[i], s=sizes[i], c=colors[i], marker=shapes[i], alpha=0.9)
	ax.legend(handles=custom_labels, loc='center left', bbox_to_anchor=(1,0.5), fontsize=8)
	ax.set_title(title, fontsize=20)
	ax.set_xlabel(xlbl)
	ax.set_ylabel(ylbl)
	LJ_points = pd.DataFrame(LJ_points, columns=['x','y'])
	GR_points = pd.DataFrame(GR_points, columns=['x','y'])
	
	confidence_ellipse(LJ_points, ax, edgecolor='#F9564F')
	confidence_ellipse(GR_points, ax, edgecolor='#3ABECF')
	#confidence_ellipse1(LJ_points['x'], LJ_points['y'], ax, edgecolor='red')
	#confidence_ellipse1(GR_points['x'], GR_points['y'], ax, edgecolor='blue')
	fig.tight_layout()
	plt.savefig(out_fname+"_full.png")
	ylimits = ax.get_ylim()
	xlimits = ax.get_xlim()
	plt.clf()
	
	snaps = {'before':"d-2 d1".split(), 'after':"d60 d30".split()}
	
	for s in snaps:  #d in day indices
		d1, d2 = snaps[s]
		fig, ax = plt.subplots(1,1,figsize=(6.4*1.5,4.8*1.5))
		LJ_points, GR_points = [], []
		for i in day_indices[d1] + day_indices[d2]:
			ax.scatter(X[i], Y[i], label=names[i], s=sizes[i], c=colors[i], marker=shapes[i], alpha=0.7)
			if names[i].find("LJ")!=-1:
				LJ_points.append([X[i],Y[i]])
			else:
				GR_points.append([X[i],Y[i]])
		
		LJ_points = np.array(LJ_points)
		GR_points = np.array(GR_points)
		
		
		LJ_gmm = confidence_ellipse(LJ_points, ax, edgecolor='#F9564F')
		GR_gmm = confidence_ellipse(GR_points, ax, edgecolor='#3ABECF')
		
		LJ_p = GR_gmm.score(LJ_points)
		GR_p = LJ_gmm.score(GR_points)
		
		ax.add_artist(AnchoredText("LJ: "+str(round(LJ_p,4))+"\nGR: "+str(round(GR_p,4)), loc=1, prop={'size': 24}))
		
		
		
		
		
		#ax.legend(handles=custom_labels, loc='center left', bbox_to_anchor=(1,0.5), fontsize=8)
		ax.set_title(title, fontsize=20)
		ax.set_xlabel(xlbl)
		ax.set_ylabel(ylbl)
		ax.set_ylim(ylimits)
		ax.set_xlim(xlimits)
		fig.tight_layout()
		plt.savefig(out_fname+"_"+s+".png")
		plt.clf()
	
	
