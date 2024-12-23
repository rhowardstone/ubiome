from regex import search
from edlib import align


def read_traces(trace_fname): # maps asv ID to list of read IDs assigned 
    traces = {}
    In = open(trace_fname)
    line = In.readline()
    while line != "":
        temp = line[:-1].split(",")
        if temp[1] in traces:
            for ele in temp[2:]:
                traces[temp[1]].append(ele)
        else:
            traces[temp[1]] = temp[2:]
        line = In.readline()
    In.close()
    return traces

def create_degenerate_string(str_in):
    degen_equiv = {'A':'A', 'C':'C', 'G':'G', 'T':'T', 'U':'T', 'R':'[AG]', 'Y':'[TC]', 'S':'[GC]', 'W':'[AT]', 'K':'[TG]', 'M':'[AC]', 'B':'[TGC]', 'D':'[ATG]', 'H':'[ATC]', 'V':'[AGC]', 'N':'[ATGC]'}
    return "".join([degen_equiv[c] for c in str_in])



rev_comp = lambda y,delta={'A':'T', 'T':'A', 'U':'A', 'G':'C', 'C':'G', 'Y':'R', 'R':'Y', 'S':'S', 'W':'W', 'K':'M', 'M':'K', 'B':'V', 'D':'H', 'H':'D', 'V':'B', 'N':'N'}:"".join([delta[x] for x in y[::-1]])

def find_all_occurrences_wOverlap(A, B, m=0):
    ''' Finds all occurrences of substring A in a larger string B\n\tOverlap allowed!\n'''
    currStr = B
    notFound = False
    offset = 0
    retval = []
    while notFound == False:
        matches = search("("+A+"){e<="+str(m)+"}", currStr)
        if matches == None or currStr == "":
            notFound = True
        else:
            begin, end = matches.span()
            index = begin
            retval.append((begin+offset, end+offset))
            currStr = currStr[index+1:]
            offset+=index+1
    return retval


def does_overlap(begin1, end1, begin2, end2):
    if begin2 < begin1:
        begin2, begin1 = begin1, begin2
        end1, end2 = end2, end1
    if end1 > begin2:
        return True
    return False

def find_all_occurrences(A, B, m=0):
    ''' Finds all occurrences of substring A in a larger string B with up to m mismatches\n\tNO OVERLAP - best matches prioritized, left to right\n'''
    retval = []
    all_matches = find_all_occurrences_wOverlap(A, B, m=m)
    DistList = {}
    for match in all_matches:
        seq = B[match[0]:match[1]]
        dist = align(A, seq)['editDistance']
        if dist in DistList:
            DistList[dist].append(match)
        else:
            DistList[dist] = [match]
    for d in sorted(list(DistList.keys())):
        for m in DistList[d]:
            toAdd = True
            for match in retval.copy():
                if does_overlap(m[0], m[1], match[0], match[1]):
                    toAdd = False
                    break
            if toAdd:
                retval.append(m) 
    return retval



def separate_fasta(fasta):
    ID_list = [ID for ID in fasta]
    seqlist = [fasta[ID] for ID in ID_list]
    return ID_list, seqlist



def read_rosetta_indexed(fname, relative=False, taxonomy=False):
	''' Returns M, indices, cols where:
 	M is a matrix with rows as samples, columns for ASVs
 	indices is a dictionary mapping all tags ('UNTR', 'd10', etc) to a set of row indices in M corresponding to those samples
 	cols is a list of column (sample) IDs
    		If taxonomy==True, return value is M, indices, cols, rows, where rows is the row IDs
	'''
	groups, days, locs = 'UNTR CMT ABX3CMT ABX10'.split(), 'd-2 d1 d3 d5 d8 d10 d30 d60'.split(), 'GR LJ'.split()
	
	sample_labels, ros = read_rosetta(fname, cols=True)  #Load, transpose, and normalize abundance matrix by sample sums
	ASV_IDs = [ID for ID in ros]
	inverted = list(zip(*[ros[ID][2] for ID in ASV_IDs]))
	del ros

	#index inverted rosetta:
	
	indices = {ele:[] for ele in groups+days+locs+['W']}
	for i in range(len(sample_labels)):
		if sample_labels[i] not in 'W1 W2'.split():  
			grp,day,loc = sample_labels[i].split("_")[:3]
			for ele in [grp,day,loc]:
				indices[ele].append(i)
		else:
			indices['W'].append(i)	#wildtype samples are 'W'
	for ele in indices:
		indices[ele] = set(indices[ele])
	if relative:
		temp = []
		for row in inverted:
			tempsum = sum(row)
			temp.append([ele/tempsum for ele in row])
		inverted = temp
	if not taxonomy:
		return inverted, indices, sample_labels
	else:
		return inverted, indices, sample_labels, ASV_IDs


def read_rosetta(fname, cols=False):
    ''' Returns dictionary mapping ASV ID to tuple (seq, tax, abund_vector)
    		If cols==True, return value is (columnIDs, {ID:(seq, tax, abund_vector)})
    '''
    In = open(fname)
    temp = [row.split(",") for row in In.read().split("\n")[1:] if row!=""]
    In.close()
    
    rosetta = {} #will map ASV ID to tuple (seq, tax, abund_vector)
    
    for row in temp:
        rosetta[row[0]] = (row[1], row[8], [int(ele) for ele in row[9:]])
    
    if cols:
        In = open(fname)
        columns = In.readline()[:-1].split(",")[9:]
        In.close()
        return (columns, rosetta)
    else:
        return rosetta
   
def read_fasta(fname):
    In = open(fname)
    temp = In.read().split("\n")
    In.close()
    fasta = {}
    for row in temp:
        if row.find(">")!=-1:
            active_seq = row[1:]
            fasta[active_seq] = ""
        else:
            fasta[active_seq] += row
    return fasta

def write_fasta(fasta, fname=None):
    Out = open(fname, "w+")
    for ID in fasta:
        Out.write(">"+ID+"\n"+fasta[ID]+"\n")
    Out.close()
    
    
def read_fastq(fname):
    In = open(fname)
    temp = In.read().split("\n")
    In.close()
    fastq = {}
    for i in range(0,len(temp),4):
        name = temp[i]
        if name!="":
            seq = temp[i+1]
            quality = temp[i+3]
            fastq[name[1:]] = (seq, quality)
    return fastq

def write_fastq(fastq, fname):
    Out = open(fname, 'w+')
    for key in fastq:
        Out.write("@"+key+"\n"+fastq[key][0]+"\n+\n"+fastq[key][1]+"\n")
    Out.close()


