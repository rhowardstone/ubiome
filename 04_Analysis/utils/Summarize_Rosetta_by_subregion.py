import sys
from utils import read_rosetta, read_fasta
from math import ceil, log10



def reverse_fasta(fasta):
    '''Returns map from sequence to list of IDs with that sequence'''
    duplists = {}
    for ID in fasta:
        if fasta[ID] not in duplists:
            duplists[fasta[ID]] = [ID]
        else:
            duplists[fasta[ID]].append(ID)
    return duplists


#SOME SAMPLES WILL NOW HAVE ZEROES - DON'T WRITE THESE!
if __name__ == "__main__":
	if len(sys.argv)!=4:
		print("Error - usage:\n >>> python3 Summarize_Rosetta_by_subregion.py [Rosetta.csv] [Subregions.fa] [Out-Rosetta.csv]\n")
		exit()
	in_fname, subregions_fname, out_fname = sys.argv[1:]
	
	Sample_IDs, ros = read_rosetta(in_fname, cols=True)
	
	subregions = reverse_fasta(read_fasta(subregions_fname)) #maps unique sequence to list of IDs of the form:     a5bab9f9f1e062bcabe20644ba93ec42.308-751  
	
	subregion_ASVIDs = {S:list(dict.fromkeys([".".join(ID.split(".")[:-1]) for ID in subregions[S]])) for S in subregions}
	
	#All_ASVs = []
	subregion_counts = {S:[0 for _ in range(len(Sample_IDs))] for S in subregions}
	for S in subregions:
		for ASV in subregion_ASVIDs[S]:
			#All_ASVs.append(ASV)
			for j in range(len(Sample_IDs)):
				subregion_counts[S][j] += ros[ASV][2][j]  #add by ASV
	
	#indices_to_drop = []
	#M = list(zip(*[subregion_counts[S] for S in subregions])) #is now by sample
	#for i in range(len(M)):
	#	if sum(M[i])==0: #sum(M[i]) >= 10 and len([1 for j in range(len(M[i])) if M[i][j]!=0])>=2: #Same filters we applied before - could also jus remove zeroes..?
	#		indices_to_drop.append(i)
	#indices_to_drop = set(indices_to_drop)
	
	Sample_IDs = [Sample_IDs[i] for i in range(len(Sample_IDs))]#  if i not in indices_to_drop]  #remove zero samples
	for S in subregions:
		subregion_counts[S] = [subregion_counts[S][i] for i in range(len(Sample_IDs))]#  if i not in indices_to_drop]
	#All_ASVs = set(All_ASVs)
	#for ID in ros:
	#	if ID not in All_ASVs:
	#		subregion_counts[ID] =   #Finish this logic if someone wants you to include the ASVs that do not have V3-V4 found.. We may wish to know their identity
	
	Out = open(out_fname, 'w+')
	Out.write('Subregion_sequence,,,,,,,,,'+",".join(Sample_IDs)+"\n")
	for S in subregions:
		Out.write(S+",,,,,,,,,"+",".join([str(ele) for ele in subregion_counts[S]])+"\n")
	Out.close()
	
	
	
	
	
	
