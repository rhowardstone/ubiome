import sys, os
from multiprocessing import Pool, cpu_count
from regex import search
from edlib import align
from glob import glob

def read_fasta_sequence(file):
    """
    Generator function to yield one sequence at a time from a FASTA file.
    """
    with open(file, 'r') as fasta_file:
        sequence_id, sequence = '', ''
        for line in fasta_file:
            line = line.strip()
            if line.startswith(">"):
                if sequence_id:
                    yield (sequence_id, sequence)
                sequence_id, sequence = line[1:], ''
            else:
                sequence += line
        # Yield the last sequence
        if sequence_id:
            yield (sequence_id, sequence)

def process_file(file, primers, m_mismatches, output_dir):
    """
    Process a single FASTA file: read sequences, find amplicons, and write to file.
    """
    amplicon_output = {}
    for sequence_id, sequence in read_fasta_sequence(file):
        amplicon_output.update(find_amplicons(sequence_id, sequence, primers, m_mismatches))
    
    # Construct an output filename based on the input file
    basename = os.path.basename(file)
    output_file = os.path.join(output_dir, f"{basename}_amplicons.fa")
    print(f"\n\n{len(amplicon_output)}\n\n")
    write_fasta(amplicon_output, output_file)

def write_fasta(amplicon_output, fname):
    """
    Write amplicons to a FASTA file.
    """
    out_file = open(fname, "w+")
    for ID in amplicon_output:
        out_file.write(f">{ID}\n{amplicon_output[ID]}\n")
    out_file.close()
    print("\nFinished", fname)

def find_amplicons(ID, sequence, primers, m_mismatches):
    """
    Find and return amplicons in the given sequence.
    """
    global forward_primer, reverse_primer
    amplicon_output = {}

    matches = {}
    for pID in primers:
        matches[ID+"\t"+pID] = find_all_occurrences(primers[pID], sequence, m=m_mismatches)

    intervals = []

    #'27f' -> 'R'
    points = {}
    for match in matches[ID+'\t27f']:
        points[match[0]-1] = '27f'
    for match in matches[ID+'\tR']:
        points[match[1]] = 'R'

    strand = list(sorted(points.keys()))
    n = 0
    for i in range(len(strand)-1):
        if points[strand[i]] == '27f' and points[strand[i+1]] == 'R':
            n+=1
            interval = str(strand[i]+len(forward_primer))+'-'+str(strand[i+1])
            amplicon_output[ID+"."+interval] = sequence[strand[i]+1:strand[i+1]]
            amplicon_output[ID+"."+interval] = amplicon_output[ID+"."+interval][len(forward_primer):-len(reverse_primer)]


    #'R_revc' -> '27f_revc'
    points = {}
    for match in matches[ID+'\t27f_revc']:
        points[match[1]] = '27f'
    for match in matches[ID+'\tR_revc']:
        points[match[0]-1] = 'R'

    strand = list(sorted(points.keys(), reverse=True))
    n = 0
    for i in range(len(strand)-1):  #extracted from StrainID amplicons which have already been corrected.. nothing *should* occur in this orientation..
        if points[strand[i]] == '27f' and points[strand[i+1]] == 'R':
            n += 1
            interval = str(strand[i])+'-'+str(strand[i+1]+len(reverse_primer))
            amplicon_output[ID+"."+interval] = rev_comp(sequence[strand[i+1]+1:strand[i]])
            amplicon_output[ID+"."+interval] = amplicon_output[ID+"."+interval][len(forward_primer):-len(reverse_primer)]
    return amplicon_output


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

rev_comp = lambda y,delta={'A':'T', 'T':'A', 'U':'A', 'G':'C', 'C':'G', 'Y':'R', 'R':'Y', 'S':'S', 'W':'W', 'K':'M', 'M':'K', 'B':'V', 'D':'H', 'H':'D', 'V':'B', 'N':'N'}:"".join([delta[x] for x in y[::-1]])

def create_degenerate_string(str_in):
    degen_equiv = {'A':'A', 'C':'C', 'G':'G', 'T':'T', 'U':'T', 'R':'[AG]', 'Y':'[TC]', 'S':'[GC]', 'W':'[AT]', 'K':'[TG]', 'M':'[AC]', 'B':'[TGC]', 'D':'[ATG]', 'H':'[ATC]', 'V':'[AGC]', 'N':'[ATGC]'}
    return "".join([degen_equiv[c] for c in str_in])


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Error - usage:\n >>> python3 Extract_StrainID_subregions_par_mem.py [input_directory] [forward-primer] [reverse-primer] [m_mismatches] [output_directory]\n")
        print("\tFor example, to get the StrainID region (16S-ITS-Partial 23S), you may use:\n\t27f: AGRRTTYGATYHTDGYTYAG\n\tR: YCNTTCCYTYDYRGTACT\n")
        exit()
    global forward_primer, reverse_primer
    input_dir, forward_primer, reverse_primer, m_mismatches, output_dir = sys.argv[1:]
    m_mismatches = int(m_mismatches)
    
    reverse_primer = rev_comp(reverse_primer)
    
    # Prepare primers
    #degen_primers = {'27f': "AGRRTTYGATYHTDGYTYAG", 'R': "AGTACYRHRARGGAANGR"}
    degen_primers = {'27f': forward_primer, 'R': reverse_primer}
    primers = {ID: create_degenerate_string(seq) for ID, seq in degen_primers.items()}
    primers.update({f"{ID}_revc": create_degenerate_string(rev_comp(seq)) for ID, seq in degen_primers.items()})

    # Find all FASTA files in the input directory
    fasta_files = glob(os.path.join(input_dir, "*"))
    
    # Process each FASTA file in parallel
    with Pool(processes=cpu_count() - 3) as pool:
        pool.starmap(process_file, [(file, primers, m_mismatches, output_dir) for file in fasta_files])

    print("\nFinished.\n")







