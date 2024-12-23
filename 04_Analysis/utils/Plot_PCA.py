import sys
import matplotlib.pyplot as plt
import matplotlib.lines as mlines


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
	Colors = {'UNTR':'#4363D8', 'ABX3FMT':'#3CB44B', 'ABX10':'#E6194B', 'FMT':'#42D4F4'}
	Shapes = {'GR':'o', 'LJ':'x'}
	#Colors = {'d60':'#000000', 'd30':'#9400D3', 'd10':'#4B0082', 'd8':'#0000FF', 'd5':'#00FF00', 'd3':'#FFFF00', 'd1':'#FF7F00', 'd0':'#FF0000'}
	
	#Shapes = {'UNTR':'o', 'ABX3FMT':'x', 'ABX10':'^', 'FMT':'s'}
	Sizes = {'GR':12, 'LJ':12}
	
	wild_size = 24
	wild_color = '#0F0A0D'
	wild_shape = '.'
	
	Sizes_legend = {'GR':5, 'LJ':10}
	
	custom_labels = []
	#for siz in Sizes:
	#	temp = mlines.Line2D([], [], color='#0000FF', marker='o', linestyle='None', markersize=Sizes_legend[siz], label=siz)
	#	custom_labels.append(temp)
	for sha in Shapes:
		temp = mlines.Line2D([], [], color='#000000', marker=Shapes[sha], linestyle='None', markersize=7, label=sha)
		custom_labels.append(temp)
	for col in Colors:
		temp = mlines.Line2D([], [], color=Colors[col], marker='o',linestyle='None', markersize=8, label=col) #markersize=loc_sizes_legend[loc]
		custom_labels.append(temp)
	
	custom_labels.append(mlines.Line2D([], [], color=wild_color, marker=wild_shape,linestyle='None', markersize=8, label='Wildtype')) #markersize=loc_sizes_legend[loc]
	
	day_indices, i = {'d60':[], 'd30':[], 'd10':[], 'd8':[], 'd5':[], 'd3':[], 'd1':[], 'd0':[]}, 0
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
			size = 24 #Sizes[lbl[2]]  #loc
			color = Colors[lbl[0]] #grp
			shape = Shapes[lbl[2]] #loc
			day_indices[lbl[1]].append(i)
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
	fig.tight_layout()
	plt.savefig(out_fname+"_full.png")
	
	ylimits = ax.get_ylim()
	xlimits = ax.get_xlim()
	
	plt.clf()
	
	for d in day_indices:
		fig, ax = plt.subplots(1,1,figsize=(6.4*1.5,4.8*1.5))
		for i in day_indices[d]:
			ax.scatter(X[i], Y[i], label=names[i], s=sizes[i], c=colors[i], marker=shapes[i], alpha=0.7)
		
		ax.legend(handles=custom_labels, loc='center left', bbox_to_anchor=(1,0.5), fontsize=8)
		ax.set_title(title, fontsize=20)
		ax.set_xlabel(xlbl)
		ax.set_ylabel(ylbl)
		ax.set_ylim(ylimits)
		ax.set_xlim(xlimits)
		fig.tight_layout()
		plt.savefig(out_fname+"_"+d+".png")
		plt.clf()
	
	
