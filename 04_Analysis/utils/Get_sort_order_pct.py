import  sys
from utils import read_rosetta


if __name__ == "__main__":
	if len(sys.argv)!=4:
		print("Error - usage:\n >>> python3 Get_sort_order_pct.py [Rosetta.csv] [tax-index] [Out.csv]\n")
		print("\tProduces [Out.csv], a list of taxa sorted by their average percentage abundance across all samples.")
		exit()
	in_fname, index, out_fname = sys.argv[1:]
	index = int(index)
	
	ros = read_rosetta(in_fname)
	All_ASVs = [ID for ID in ros]
	M = [ros[ID][2] for ID in All_ASVs] #rows are ASVs
	M = list(zip(*M)) #Rows are samples
	temp = []
	for i in range(len(M)):
		tot = sum(M[i])
		temp.append([M[i][j]/tot for j in range(len(M[i]))])
	M = list(zip(*temp)) #rows are ASVs again
	for i in range(len(All_ASVs)):
		ID = All_ASVs[i]
		ros[ID] = (ros[ID][0], ros[ID][1], M[i])
	
	totals = {}
	
	for ID in ros:
		temp = ros[ID][1].split(";")
		if len(temp) == 1:
			tax = temp[0]
		else:
			tax = temp[index]
		if tax in totals:
			for ele in ros[ID][2]:
				totals[tax].append(ele)
		else:
			totals[tax] = [ele for ele in ros[ID][2]]
	
	avg = {}
	for tax in totals:
		tot = sum(totals[tax])
		avg[tax] = tot/len(totals[tax])
	
	order = sorted(avg, key = lambda x:avg[x])
	
	#tot = sum([totals[tax] for tax in totals])
	
	Out = open(out_fname, "w+")
	for tax in totals:
		Out.write(",".join([str(ele) for ele in [tax, len(totals[tax]), avg[tax]]])+'\n')
	#Out.write("\n".join(order)+"\n")
	Out.close()
		
	
