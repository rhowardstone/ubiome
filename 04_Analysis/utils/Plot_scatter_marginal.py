import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

def main():
	if len(sys.argv) != 12:
		print("Error - usage:\n >>> python3 Plot_scatter_marginal.py [In.tsv] [0/1 Headers?] [delim] [ind-x] [ind-y] [ind-series] [log-x (0/1)] [log-y (0/1)] [xlabel] [ylabel] [Out.png]\n")
		sys.exit(1)

	in_fname, headers, delim, ind_x, ind_y, ind_ser, log_x, log_y, xlbl, ylbl, out_fname = sys.argv[1:]
	ind_x, ind_y, ind_ser = int(ind_x), int(ind_y), int(ind_ser)
	log_x, log_y = int(log_x), int(log_y)

	# Read data
	data = pd.read_csv(in_fname, delimiter=delim if delim != '\\t' else '\t', header=0 if headers == '1' else None)

	# Validate indices
	if max(ind_x, ind_y, ind_ser) >= data.shape[1]:
		print("Index error: Please check your column indices.")
		sys.exit(1)

	# Assign column names if headers are not used
	if headers == '0':
		data.columns = [f'Column_{i}' for i in range(data.shape[1])]
	
	Xname = data.columns[ind_x]
	Yname = data.columns[ind_y]
	Sname = data.columns[ind_ser] if ind_ser != -1 else None

	# Prepare bins for marginal histograms
	if log_x:
		min_x_value = data[Xname].min()
		if min_x_value <= 0:
			min_x_value = min(filter(lambda x: x > 0, data[Xname]), default=0.1)
		max_x_value = data[Xname].max()
		bins_x = np.logspace(np.log10(min_x_value), np.log10(max_x_value), 25)
	else:
		bins_x = 25

	if log_y:
		min_y_value = data[Yname].min()
		if min_y_value <= 0:
			min_y_value = min(filter(lambda x: x > 0, data[Yname]), default=0.1)
		max_y_value = data[Yname].max()
		bins_y = np.logspace(np.log10(min_y_value), np.log10(max_y_value), 25)
		# Set the Y-axis range for marginal histograms
		
	else:
		bins_y = 25

	# Plotting

	# Prepare your data here (as previously)
	# data, Xname, Yname, etc.

	# Create a JointGrid
	g = sns.JointGrid(data=data, x=Xname, y=Yname, hue=Sname if ind_ser != -1 else None)

	# Plot scatter on the joint part of the grid
	g.ax_joint.scatter(data[Xname], data[Yname], color="blue", alpha=0.4, s=1.2)

	# Plot histograms on the marginal axes
	g.ax_marg_x.hist(data[Xname], bins=bins_x, color="blue", alpha=0.6)
	g.ax_marg_y.hist(data[Yname], bins=bins_y, orientation="horizontal", color="blue", alpha=0.6) #, log=True)
	
	if log_x:
		g.ax_joint.set_xscale('log')
		g.ax_marg_x.set_xscale('log')
	
	if log_y:
		g.ax_joint.set_yscale('log')
		g.ax_marg_y.set_yscale('log')

	# Optionally add labels and titles as needed
	if xlbl == '':
		xlbl = Xname
	if ylbl == '':
		ylbl = Yname
	
	g.set_axis_labels(xlbl, ylbl, fontweight='bold', fontsize=16)
	# Customize tick labels for the main joint plot
	# Customize tick labels for the main joint plot
	for label in g.ax_joint.get_xticklabels():
		label.set_fontsize(13)
		label.set_fontweight('bold')

	for label in g.ax_joint.get_yticklabels():
		label.set_fontsize(13)
		label.set_fontweight('bold')


	# Customize tick labels for the main joint plot
	#g.ax_joint.tick_params(axis='both', which='both', labelsize=14, labelcolor='black', labelrotation=0, labelweight='bold')

	# Save the plot
	plt.tight_layout()
	plt.savefig(out_fname)
	plt.close()

	print(f"Plot saved to {out_fname}")



if __name__ == "__main__":
	main()

