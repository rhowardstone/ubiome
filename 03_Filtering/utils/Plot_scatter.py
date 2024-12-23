import sys
import matplotlib.pyplot as plt

if __name__ == "__main__":
	if len(sys.argv)!=13:
		print("Error - usage:\n >>> python3 Plot_scatter.py [In.tsv] [0/1 Headers?] [delim] [ind-x] [ind-y] [ind-series] [0/1 xLog?] [0/1 yLog?] [0/1 Interpolate?] [x-label] [y-label] [Out.png]\n")
		print("\tIndices are 0-based.\n")
		exit()
	in_fname, headers, delim, ind_x, ind_y, ind_ser, xlog, ylog, interp, xlbl, ylbl, out_fname = sys.argv[1:]
	ind_x, ind_y, ind_ser = int(ind_x), int(ind_y), int(ind_ser)
	delim = '\t'
	
	print("Delim is:", delim)
	
	Xname, Yname, x, y = xlbl, ylbl, {}, {}
	if ind_ser == -1:
		x[0], y[0] = [], []
		
	In = open(in_fname)
	line = In.readline()
	if headers == '1':
		temp = line[:-1].split(delim)
		if xlbl == '':
			Xname = temp[ind_x]
		if ylbl == '':
			Yname = temp[ind_y]
		Sname = temp[ind_ser]
		line = In.readline()
	while line != "":
		temp = line[:-1].split(delim)
		if temp[ind_x] != '' and temp[ind_y] != '':
			if ind_ser != -1:
				S = int(temp[ind_ser])
				if S in x:
					x[S].append(float(temp[ind_x]))
					y[S].append(float(temp[ind_y]))
				else:
					x[S] = [float(temp[ind_x])]
					y[S] = [float(temp[ind_y])]
			else:
				x[0].append(float(temp[ind_x]))
				y[0].append(float(temp[ind_y]))
		line = In.readline()
	In.close()
	
	
	fig, ax = plt.subplots()
	#ax.set_xscale('log', base=2)
	#ax.set_yscale('log', base=2)
	if ind_ser != -1:
		for S in sorted(x):
			if interp == '0':
				ax.scatter(x[S], y[S], s=2, label=S, alpha=0.8)
			else:
				ax.plot(x[S], y[S], label=S, alpha=0.8)
		#plt.scatter(x, y, s=5)
		ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	else:
		X = x[sorted(x)[0]]
		for S in sorted(x)[1:]:
			X += x[S]
		Y = y[sorted(y)[0]]
		for S in sorted(y)[1:]:
			Y += y[S]
		if interp == '0':
			ax.scatter(X, Y, s=2, alpha=0.8)
		else:
			ax.plot(X, Y, alpha=0.8)
	
	ax = plt.gca()

	# Set y-axis tick labels to bold
	for label in ax.get_yticklabels():
		label.set_fontweight('bold')
	for label in ax.get_xticklabels():
		label.set_fontweight('bold')

	
	if xlog == '1':
		ax.set_xscale('log')
	if ylog == '1':
		ax.set_yscale('log')
	
	plt.xlabel(Xname, fontsize=16, fontweight='bold')
	plt.ylabel(Yname, fontsize=16, fontweight='bold')
	plt.savefig(out_fname)
	
