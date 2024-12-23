import matplotlib.pyplot as plt
import matplotlib.patches as patches

import sys
#fdbbb9   #e789e7  #b0e5ec 
def draw_rectangular_venn(ax, sizeA, sizeI, sizeB, scale=10, H=4, colA='#F9564F', colI='#801A80', colB='#3ABECF', edges='none', fontsize=32):
	# Define widths of the rectangles and the plot scale
	tot = sizeA + sizeI + sizeB
	#scale, H = 10, 4
	widthA, widthI, widthB = [x / tot * scale for x in (sizeA, sizeI, sizeB)]

	# Draw the rectangles
	rectA = patches.Rectangle((0, 0), widthA, H, facecolor=colA, edgecolor='None')
	rectI = patches.Rectangle((widthA, 0), widthI, H, facecolor=colI, alpha=0.6, edgecolor='None')
	rectB = patches.Rectangle((widthA + widthI, 0), widthB, H, facecolor=colB, edgecolor='None')
	
	# Add the rectangles to the axes
	for rect in [rectA, rectI, rectB]:
		ax.add_patch(rect)

	# Set the aspect of the plot and the limits
	ax.set_aspect('equal', 'box')
	ax.set_xlim(0, scale)
	ax.set_ylim(0, H)

	# Create the FancyBboxPatch as a clipping patch
	if edges == 'none':
		fancy_clip_path = patches.FancyBboxPatch((0, 0), scale, H, boxstyle="round,pad=0.02,rounding_size=0.5", facecolor='none', clip_on=False)
	else:
		fancy_clip_path = patches.FancyBboxPatch((0, 0), scale, H, boxstyle="round,pad=0.02,rounding_size=0.5", linestyle=edges, edgecolor='black', linewidth=3, facecolor='none', clip_on=False)
		
	ax.add_patch(fancy_clip_path)

	# Apply the FancyBboxPatch as the clipping path to the rectangles
	for rect in [rectA, rectI, rectB]:
		rect.set_clip_path(fancy_clip_path)

	# Add text labels
	if edges == 'none':  #is this ever used ..?
		ax.text(scale / 48, H / 2, format(sizeA,",d"), fontsize=fontsize, fontweight='bold', ha='left', va='center', color='black') #prop={'size':72})
		ax.text(widthA + widthI / 2, H / 2, format(sizeI,",d"), fontsize=fontsize, fontweight='bold', ha='center', va='center', color='black')
		ax.text(scale*47/48, H / 2, format(sizeB,",d"), fontsize=fontsize, fontweight='bold', ha='right', va='center', color='black')
	else:
		tot = sizeA+sizeI+sizeB
		if sizeA/tot > 0.02:
			ax.text(scale / 48, H / 2, "{:.0f}%".format(100*sizeA/tot), fontsize=fontsize, fontweight='bold', ha='left', va='center', color='black')
		if sizeI/tot > 0.95:
			ax.text(widthA + widthI / 2, H / 2, "{:.1f}%".format(100*sizeI/tot), fontsize=fontsize, fontweight='bold', ha='center', va='center', color='black')
		else:
			ax.text(widthA + widthI / 2, H / 2, "{:.0f}%".format(100*sizeI/tot), fontsize=fontsize, fontweight='bold', ha='center', va='center', color='black')
		if sizeB/tot > 0.02:
			ax.text(scale*47/48, H / 2, "{:.0f}%".format(100*sizeB/tot), fontsize=fontsize, fontweight='bold', ha='right', va='center', color='black')
	# Hide the axes
	ax.axis('off')


if __name__ == "__main__":
	if len(sys.argv) < 9:
		print("Error - usage:\n >>> python3 Plot_venn_rectangles.py [out_fname.png] [A] [intersection] [B] [0/1 outline?] [width] [height] [fontsize] [optional: colA] [optional: colI] [optional: colB]\n")
		exit()
	
	
	
	
	print(sys.argv)
	
	
	out_fname = sys.argv[1]
	A, I, B = [float(ele) for ele in sys.argv[2:5]]
	edges = 'dashed' if sys.argv[5]=='1' else 'solid'
	width, height = [float(e) for e in sys.argv[6:8]]
	fontsize = int(sys.argv[8])
	if len(sys.argv)>9:
		colA, colI, colB = sys.argv[9:12]
	else:
		colA, colI, colB = '#F9564F', '#801A80', '#3ABECF'


	
	fig, ax = plt.subplots()
	draw_rectangular_venn(ax, A, I, B, scale=width, H=height, colA=colA, colI=colI, colB=colB, edges=edges, fontsize=fontsize)
	
	plt.savefig(out_fname)










