from HYPeTools.alignment.semiglobal import semiglobal_matrix
import numpy as np

def find_in_read(dna, read):
    # get the most likely position of a sub-sequence in a read and the normalized alignment score
    scores = semiglobal_matrix(dna, read)[-1, :]
    score = max(scores)/len(dna)
    pos = np.argmax(scores)

    return pos, score

def extract_hvd_from_read(read, start, end, threshold = 0.5, rev = True):
    
    # find the start and end of the HVD in the read
    start_pos, start_score = find_in_read(start, read)
    end_pos, end_score = find_in_read(end, read)


    # if scores are too low, try reverse complement
    if rev and (start_score < threshold or end_score < threshold):
        # create reverse complement
        complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
        rev_comp = ''.join(complement[base] for base in reversed(read))
        
        # check scores with reverse complement
        start_pos_rc, start_score_rc = find_in_read(start, rev_comp)
        end_pos_rc, end_score_rc = find_in_read(end, rev_comp)
        
        # use reverse complement if scores are better
        if start_score_rc > start_score and end_score_rc > end_score:
            read = rev_comp
            start_pos = start_pos_rc
            end_pos = end_pos_rc
            start_score = start_score_rc 
            end_score = end_score_rc

    # if scores are still too low, return empty string
    if start_score < threshold or end_score < threshold:
        return "", "", ""
        
    # verify the HVD boundaries make sense
    if (end_pos - len(end) - start_pos) < 0:
        return "", "", ""

    # return the HVD
    return read[start_pos:end_pos - len(end)], read[:start_pos], read[end_pos -  len(end):]