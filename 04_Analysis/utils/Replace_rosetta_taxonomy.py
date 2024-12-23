import sys

if __name__ == "__main__":
	if len(sys.argv)!=4:
		print("Error - usage:\n >>> python3 [Rosetta_in.csv] [Athena_DB.tax] [Rosetta_out.csv]\n")
		exit()
	in_fname, db_fname, out_fname = sys.argv[1:]
	
	
	In = open(db_fname)
	temp = [row.split("\t") for row in In.read().split("\n") if row!=""]
	In.close()
	DB = {}
	for row in temp:
		tax = row[1].split(";")[:-1]
		fill = 'Unclassified_'+tax[-1]
		for i in range(len(tax),8):
			tax.append(fill)
		
		DB[row[0]] = ";".join(tax)

	
	replaced, not_replaced = 0, 0
	unc_replaced, unc_not = 0, 0
	
	not_replaced_list = []
	
	In = open(in_fname)
	Out = open(out_fname, 'w+')
	
	Header = In.readline().replace("_d0_","_d-2_").replace('FMT','CMT')  #bandaid -- *will* likely break things - keep a close eye
	Out.write(Header)
	
	line = In.readline()
	while line != "":  #index 2 is ID, 8 is tax
		row = line[:-1].split(",")
		ID = row[2]#.split(".")
		#if len(ID)>1:
		#	ID = ".".join(ID)
		#else:
		#	ID = ID[0]
		
		if ID in DB:
			if row[8].lower().find('unclassified')!=-1:
				unc_replaced += 1
			replaced += 1
			row[8] = DB[ID]
			
		else:
			if row[8].lower().find('unclassified')!=-1:
				unc_not += 1
			not_replaced += 1
			not_replaced_list.append(row[2])
		Out.write(",".join(row)+"\n")
		line = In.readline()
	In.close()
	Out.close()
	
	
	print()
	print(not_replaced_list[:5])
	
	print()
	print("Replaced:", replaced, "\tunclassified:", unc_replaced, sep='\t')
	print("Not replaced:", not_replaced, "\tunclassified:", unc_not, sep='\t')
	print("Total:", replaced+not_replaced)
	print()
