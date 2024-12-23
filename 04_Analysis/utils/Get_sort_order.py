import  sys
from utils import read_rosetta


if __name__ == "__main__":
	if len(sys.argv)!=4:
		print("Error - usage:\n >>> python3 Get_sort_order.py [Rosetta.csv] [tax-index] [Out.csv]\n")
		exit()
	in_fname, index, out_fname = sys.argv[1:]
	index = int(index)
	
	ros = read_rosetta(in_fname)
	
	totals = {}
	
	for ID in ros:
		temp = ros[ID][1].split(";")
		if len(temp) == 1:
			tax = temp[0]
		else:
			tax = temp[index]
		if tax in totals:
			totals[tax] += sum(ros[ID][2])
		else:
			totals[tax] = sum(ros[ID][2])
	
	order = sorted(totals, key = lambda x:totals[x])
	
	tot = sum([totals[tax] for tax in totals])
	
	Out = open(out_fname, "w+")
	for tax in totals:
		Out.write(",".join([str(ele) for ele in [tax, totals[tax], totals[tax]/tot]])+'\n')
	#Out.write("\n".join(order)+"\n")
	Out.close()
		
	
