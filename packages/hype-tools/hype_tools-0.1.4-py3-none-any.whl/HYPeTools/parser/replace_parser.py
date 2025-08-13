import pandas as pd
from HYPeTools.alignment.semiglobal import semiglobal_matrix
from itertools import chain, combinations, product
from HYPeTools.utils import find_fastas, read_fasta, dumb_consensus
from .utils import read_motifs, translate_motif, create_output_filename, write_results
from HYPeTools.HVD.utils import extract_hvd_from_read
import os
from tqdm import tqdm
import logging

def find_and_replace_motifs(read, motifs):
    """
    Find exact matches of motifs in read and replace them with blanks.
    Returns the modified read and a DataFrame of replaced motifs.
    """
    # Create DataFrame with columns: start pos, end pos, original_dna, best_fitting_motif_dna
    replaced_motifs = pd.DataFrame(columns=['start_pos', 'end_pos', 'original_dna', 'motif', 'alignment_score'])

    for motif_dna in motifs:
        # Find all occurrences of the motif in the read
        start = 0
        while True:
            pos = read.find(motif_dna, start)
            if pos == -1:  # No more occurrences found
                break
            end_pos = pos + len(motif_dna)
            # Append a new row to the DataFrame
            new_row = pd.DataFrame({
                'start_pos': [pos],
                'end_pos': [end_pos], 
                'original_dna': [read[pos:end_pos]],
                'motif': [motif_dna], 
                'alignment_score': 1
            })
            replaced_motifs = pd.concat([replaced_motifs, new_row], ignore_index=True)
            start = pos + 1

    # If two motifs have overlapping positions, remove both 
    # Sort the replaced motifs by start position
    replaced_motifs = replaced_motifs.sort_values('start_pos').reset_index(drop=True)

    # Check if row i+1 has an overlapping start_pos with row i end_pos
    # Check for overlapping motifs - keep the motifs to give some credit to the nucleotide that fits for both, 
    # but ajust the start and end positions as if it was not there (to deal with this conservatively) 
    # Ideally this would have been done with an approach to find the best configuration, but this increases the runtime exponentially
    for i in range(len(replaced_motifs) - 1):
        if replaced_motifs.iloc[i+1]['start_pos'] < replaced_motifs.iloc[i]['end_pos']:
            replaced_motifs.iloc[i]['end_pos'] = replaced_motifs.iloc[i]['end_pos'] -1
            replaced_motifs.iloc[i+1]['start_pos'] = replaced_motifs.iloc[i+1]['start_pos'] + 1
            replaced_motifs.iloc[i]['alignment_score'] = (len(replaced_motifs.iloc[i]['motif']) - 1)/len(replaced_motifs.iloc[i]['motif'])
            replaced_motifs.iloc[i+1]['alignment_score'] = (len(replaced_motifs.iloc[i+1]['motif']) - 1)/len(replaced_motifs.iloc[i+1]['motif'])


    # Create a copy of the original read
    modified_read = list(read)

    # Replace each found motif with blanks
    for _, row in replaced_motifs.iterrows():
        start = row['start_pos']
        end = row['end_pos']
        # Replace characters with blanks
        for i in range(start, end):
            modified_read[i] = ' '

    # Convert the list back to a string
    modified_read = ''.join(modified_read)
    return modified_read, replaced_motifs




def calculate_alignment_scores(modified_read, motifs):

    # Get the alignment scores forward and reverse
    # Get alignment scores for forward and reverse sequences
    forward_scores = {}
    reverse_scores = {}

    # For each motif, calculate alignment scores for both forward and reverse complement
    for motif_dna in motifs:
        # Forward alignment
        alignment_matrix = semiglobal_matrix(motif_dna, modified_read)
        forward_scores[motif_dna] = alignment_matrix[-1,:] / len(motif_dna)
        
        # Reverse complement alignment
        alignment_matrix = semiglobal_matrix(motif_dna[::-1], modified_read[::-1]) 
        reverse_scores[motif_dna] = (alignment_matrix[-1,:] / len(motif_dna))[::-1]
   
    return forward_scores, reverse_scores


def find_matching_scores(read, motifs, forward_scores, reverse_scores, threshold=0.6): # TODO: try different thresholds
        # Match forward and reverse scores for each motif
        matches = []
        for motif_dna in motifs:
            forward = forward_scores[motif_dna]
            reverse = reverse_scores[motif_dna]
            
            for rev_pos, rev_score in enumerate(reverse):
                # Skip if score is below threshold
                if rev_score < threshold:
                    continue

                for fwd_pos in range(rev_pos + 1 + int(len(motif_dna) * 0.5), min(rev_pos + 1 + int(len(motif_dna) * 1.5), len(forward))):
                    fwd_score = forward[fwd_pos]
                    # Skip if score is below threshold
                    if fwd_score < threshold:
                        continue

                        
                    if abs(fwd_score - rev_score) < 0.0001:  # Use small threshold for float comparison
                        # Convert reverse position back to original coordinates
                        
                        # Check if the original dna is including blanks (gaps at the start or end of the motif) if so adjust the start and end positions
                        while ' ' in read[rev_pos:fwd_pos]:
                            if read[rev_pos] == ' ':
                                rev_pos += 1
                            if read[fwd_pos-1] == ' ':
                                fwd_pos -= 1
                            
                        matches.append({
                            'motif': motif_dna,
                            'score': fwd_score,
                            'end_pos': fwd_pos,
                            'start_pos': rev_pos,
                            'original_dna': read[rev_pos:fwd_pos]
                        })
                        break
        return matches

def group_matches_into_intervals(matches):
    """Group overlapping matches into the same interval"""
        
    # Sort intervals by the starting point
    matches.sort(key = lambda x: x['start_pos'])

    # Iterate through the sorted intervals and check for gaps
    if len(matches) == 0:
        return []
    current_start, current_end = (matches[0]['start_pos'], matches[0]['end_pos'])
    current_id = 0

    intervals = []
    for i, match in enumerate(matches):
        start, end = (match['start_pos'], match['end_pos'])
        # If the start of the next interval is greater than the current end, there's a gap
        if start > current_end:
            intervals.append(matches[current_id:i])
            current_id = i
        # Otherwise, merge the intervals by extending the current end
        current_end = max(current_end, end)

    # Add the last interval
    intervals.append(matches[current_id:])
    # If no gaps were found, the union is a single closed interval
    return intervals

def is_overlapping(match1, match2):
    # Check if two matches overlap based on their start and end positions   

    if (match1['end_pos'] > match2['start_pos'] and match1['start_pos'] <= match2['start_pos']) or \
       (match1['start_pos'] < match2['end_pos'] and match1['end_pos'] >= match2['end_pos']):
        return True
    
    return False

def powerset(iterable):
    '''create the powerset for a given set'''

    s = list(iterable)
    return chain.from_iterable(
            combinations(s, r) for r in range(len(s) + 1))


def get_possible_configurations(matches):
    ''' With a given list of matches generate all configurations of those matches
    where there are no two matches overlapping '''

    # TODO this might be more efficiently by using a dynamic programming approach

    all_configs = list(powerset(matches))

    possible_configs = []
    for config in all_configs:
        has_overlap = False
        # Remove all configurations where matches are overlapping
        for i,j in list(product(range(len(config)),range(len(config)))):
            if is_overlapping(config[i], config[j]) and not i == j:
                has_overlap = True
                break
        if not has_overlap:
            possible_configs.append(config)

    return possible_configs


def get_best_configuration(interval):
            """
            Get the best configuration for a given interval as the interval with the highest product of covered bases * their alignment score
            """
            # The runtime is exponential in the length of the interval, so we need to limit the length of the interval
            while len(interval) > 17:
                # If we have matches with the same position, but one with lower alignment score, remove the one with the lower alignment score
                for i,j in list(product(range(len(interval)),range(len(interval)))):
                    if interval[i]['start_pos'] == interval[j]['start_pos'] and interval[i]['end_pos'] == interval[j]['end_pos'] and interval[i]['score'] < interval[j]['score']:
                        interval.remove(interval[i])
                        break
                
                # If no two matches have the same position, remove the match with the lowest alignment score
                interval.remove(min(interval, key=lambda x: x['score']))

            possible_configs = get_possible_configurations(interval)

            # Calculate the best possible configurations
            best_configs = []

            for config in possible_configs:
                # Calculate the cummulative adjusted alignment score for the configuration
                cummulative_score = 0
                for match in config:
                    cummulative_score += match['score'] * len(match['original_dna'])
                best_configs.append({
                    'config': config,
                    'score': cummulative_score
                })

            # Get the best configuration 
            # get all configs with the highest cumulated alignmentscore
            best_configs = [config for config in best_configs if config['score'] == max(config['score'] for config in best_configs)]
            # if there are multiple best configs, disambiguate them
            if len(best_configs) > 1:
                best_config = disambiguate_configs(best_configs)
            # return a random config from the best configs 
            else:
                best_config = best_configs[0]

            return best_config

def add_best_config_to_replaced_motifs(best_config, replaced_motifs):
    """Add matches from best configuration to replaced_motifs DataFrame"""
    for match in best_config['config']:
        new_row = pd.DataFrame({
            'start_pos': [match['start_pos']],
            'end_pos': [match['end_pos']], 
            'original_dna': [match['original_dna']],
            'motif': [match['motif']],
            'alignment_score': [match['score']]
        })
        replaced_motifs = pd.concat([replaced_motifs, new_row], ignore_index=True)
    return replaced_motifs

def disambiguate_configs(configs):
    """Compare dna of the configurations at each position, and return the consensus dna sequence"""

    # First Case: All configs have the same dna motifs
    # If so, return the first config
    motifs_2D = []
    all_same = True
    for config in configs:
        motifs_2D.append(get_motifs_from_config(config['config']))
        
        for i in range(len(motifs_2D[0])):
            if not all(motifs_2D[j][i] == motifs_2D[0][i] for j in range(len(motifs_2D))):
                all_same = False
                break
        if not all_same:
            break
    if all_same:
        return configs[0]

    # Second and third case: The motifs are different
    # Check if the positions of original_dna are the same
    positions_2D = []
    all_same = True
    for config in configs:
        positions_2D.append(get_positions_from_config(config['config']))
        
        for i in range(len(positions_2D[0])):
            if not all(positions_2D[j][i] == positions_2D[0][i] for j in range(len(positions_2D))):
                all_same = False
                break
        if not all_same:
            break

    # Second Case: the positions of original_dna are the same, but the dna motifs are different
    # If so, find the positions where the dna differs and return the consensus dna sequence
    if all_same:
        motifs_2D = []
        # Go through all configs and compare all motifs and get the consensus motif
        consensus_motifs = []
        for config in configs:
            motifs_2D.append(get_motifs_from_config(config['config']))
    # Third Case: the positions of original_dna are different and the dna motifs are different
    else:
        # This case is very rare ( < 1:250 reads ) so we just return an empty config
        return {'config': (), 'score': 0}
     


    for i in range(len(motifs_2D[0])):
        consensus_motifs.append(dumb_consensus([motifs_2D[j][i] for j in range(len(motifs_2D))]))
    # Build a consensus config from the consensus motifs and the positions
    consensus_config = []
    for i in range(len(consensus_motifs)):
        consensus_config.append({
            'motif': consensus_motifs[i],
            'start_pos': positions_2D[0][i][0],
            'end_pos': positions_2D[0][i][1],
            'original_dna': configs[0]['config'][i]['original_dna'],
            'score': configs[0]['config'][i]['score']
        })
    return {'config': tuple(consensus_config), 'score': configs[0]['score']}



def get_motifs_from_config(config):
    motifs = []
    for item in config:
        motifs.append(item['motif'])
    return motifs

def get_positions_from_config(config):
    positions = []
    for item in config:
        positions.append((item['start_pos'], item['end_pos']))
    return positions

def calculate_coverage(replaced_motifs, read):
    # Calculate the percentage of the read that is covered by the replaced motifs
    covered_bases = sum((row['end_pos']  - row['start_pos']) for _, row in replaced_motifs.iterrows())

    if len(read) == 0 or covered_bases == 0:
        return 0
    return covered_bases / len(read)



def get_quality_score(row, motifs):
    # If the row is an empty Series return None
    # Check if row is empty (like Series([], dtype: float64))
    if row.empty or len(row) == 0:
        return None

    # If the motif is not in the list of motifs, return a low quality score
    if not row['motif'] in motifs:
        return 1

    motif_scores = {}

    # Calculate alignment scores for the remaining motifs
    forward_scores, reverse_scores = calculate_alignment_scores(row['original_dna'], motifs)

    # Find matching alignment scores to determine the motif positions
    matches = find_matching_scores(row['original_dna'], motifs, forward_scores, reverse_scores, threshold=0.5)

    # Get the matches where the positions are no more then the length of original_dna apart
    matches = [match for match in matches if match['end_pos'] - match['start_pos'] <= len(row['original_dna'])]

    # Get the motif scores for the matches
    for match in matches:
        motif_scores[match['motif']] = match['score']

    
    current_score = row['alignment_score']
    
    # Find the second highest score
    second_best_score = 0
    for motif, score in motif_scores.items():
        if motif != row['motif'] and score > second_best_score:
            second_best_score = score
    
    # If there's no second best score or it's 0, return a high quality score
    if second_best_score == 0:
        return 2.0  # or another suitable value to indicate high confidence
    
    # Calculate quality as ratio of current score to second best
    quality_score = current_score / second_best_score
    
    return quality_score

def replace_main(motifs_file, hvds_file, input_path, start_index, end_index):

    ## ------------------------------------------------ Setup -------------------------------------------------- ##


    # If the input path is a file
    if os.path.isfile(input_path):
        fasta_files = [input_path]
        output_files = [create_output_filename(input_path, start_index, end_index)]
       

    # If the input path is a folder
    elif os.path.isdir(input_path):
        fasta_files = find_fastas(input_path)
        output_files = [create_output_filename(fasta_file, start_index, end_index) for fasta_file in fasta_files]




    # Read motifs
    motifs = read_motifs(motifs_file)
    # Read start and end markers
    (_, hvd_start), (_, hvd_end) = read_fasta(hvds_file)

    # Get all the relevant fasta files
    fasta_files = find_fastas(input_path)

    # Set logging level
    logging.basicConfig(level=logging.INFO)


    ## ----------------------------------------- Process fasta files ------------------------------------------- ##

    for fasta_file, output_file in zip(fasta_files, output_files):

        logging.info(f"Processing {fasta_file}")
        logging.info(f"Writing to {output_file}")

        # If the output file already exists, skip the processing
        if os.path.exists(output_file):
            print(f"Skipping: \n{fasta_file} \nOutput file already exists.")
            continue

        # Create output file
        with open(output_file, 'w') as f:
            pass

        # Read fasta file
        fasta_reader = read_fasta(fasta_file)

        # Get total number of sequences by counting lines in file
        total_seqs = sum(1 for line in open(fasta_file) if line.startswith('>'))

        # Iterate over all the sequences one by one
        for idx, (header, read) in enumerate(tqdm(fasta_reader, total=total_seqs, desc="Processing sequences", unit="%")):

            # Only process sequences within the specified range
            if idx < start_index or idx > end_index:
                continue

            # Extract the HVD
            read, _, _ = extract_hvd_from_read(read, hvd_start, hvd_end)
            
            ## ------------------------------------------------ Find the Motifs ------------------------------------------------ ##

            # Replace perfect matches with blanks
            modified_read, replaced_motifs = find_and_replace_motifs(read, motifs)

            # Calculate alignment scores for the remaining motifs
            forward_scores, reverse_scores = calculate_alignment_scores(modified_read, motifs)

            # Find matching alignment scores to determine the motif positions
            matches = find_matching_scores(modified_read, motifs, forward_scores, reverse_scores)

            # Find out which matches are actually overlapping and adress each intervall individually
            disjunct_intervals = group_matches_into_intervals(matches)

            # Process each disjunct interval individually
            for interval in disjunct_intervals:
                best_config = get_best_configuration(interval)
                replaced_motifs = add_best_config_to_replaced_motifs(best_config, replaced_motifs)

            ## ------------------------------------------------ Finalize ------------------------------------------------ ##

            # Sort the replaced motifs by start position
            replaced_motifs = replaced_motifs.sort_values('start_pos').reset_index(drop=True)

            # Translate the motifs into amino acids
            replaced_motifs['amino_acid'] = replaced_motifs['motif'].apply(translate_motif, motifs_table=motifs)

            # Get the quality score of the replaced motifs
            replaced_motifs['quality_score'] = replaced_motifs.apply(get_quality_score, axis=1, motifs=motifs)

            # Get the percentage of the read that is covered by the replaced motifs
            coverage = calculate_coverage(replaced_motifs, read)

            # Get the average alignment score of the replaced motifs
            average_alignment_score = sum(replaced_motifs['alignment_score'])/len(replaced_motifs) if len(replaced_motifs) > 0 else -1

            # Write results to output file
            write_results(output_file, header, read, replaced_motifs, coverage, average_alignment_score)




    
