"""
Create a synthetic data set to mimick real observed HYP1 reads.

The synthetic data set contains:
- real observed HYP1 reads - sampled from real data
- hybrid reads - created by combining two real observed HYP1 reads
- block-based reads - created by combining a random number of motifs, but following the block arrangement of real observed HYP1 reads
- random motif-based reads - created by combining a random number of motifs

These are created and then mutated, which means indels and SNPs are introduced.
The mutation rate is on a per base pair basis. The rate is sampled from a normal distribution to resemble the mutation rate of real observed HYP1 reads.
the actually observed HYPs. It is chosen in such a way that the number of reads without indels and SNPs is approximately the same as the number in the real observed HYP1 data set.


The synthetic data set also contains:
- severely mutated sequences - created by mutating the real observed HYP1 reads
- completely random sequences - created by randomly combining bases

The length of the sequences are sampled from a normal distribution to resemble the length of real observed HYP1 reads.
For the block-based and random motif-based sequences, this length is obtained by using the length of unique real obsereved HYP reads

The user can provide files containing:
- real observed HYP1 reads
- motifs
- conserved regions (Those may be appende)

The user can also specify the number of sequences to generate for each category.
"""

import argparse
import logging
import random
from Bio import SeqIO
import numpy as np
import pandas as pd
from typing import List
from Bio.Seq import Seq
from dataclasses import dataclass
from tqdm import tqdm
import os
import Levenshtein 
import warnings

# Suppress pandas warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None  # default='warn'

@dataclass
class NumbersConfig:
    mean_blocks: float = 5.3
    std_blocks: float = 1.7
    mean_motifs_per_block: float = 3.5
    std_motifs_per_block: float = 0.4
    mean_motifs: float = 20
    std_motifs: float = 6
    random_mean_lenght: float = 355
    random_std_lenght: float = 103



def load_sequences(fasta_path):
    """Load sequences from a FASTA file"""
    sequences = []
    with open(fasta_path, 'r') as f:
        for line in f:
            if not line.startswith('>'):
                sequences.append(line.strip())
    return sequences


def load_motifs(fasta_path):
    """Load the motifs and their headers"""
    motifs = []
    for record in SeqIO.parse(fasta_path, "fasta"):
        motifs.append(record)
    return motifs

def load_conserved(fasta_path):
    """Load the conserved regions from a FASTA file"""
    start = None
    end = None
    
    for record in SeqIO.parse(fasta_path, "fasta"):
        if "start" in record.description:
            start = str(record.seq)
        elif "end" in record.description:
            end = str(record.seq)
            
    if start is None or end is None:
        raise ValueError("Both start and end conserved regions must be provided in the FASTA file" +
                         "with the description 'start' and 'end' in the header respectively")
    return start, end

def create_hybrid_sequence(seq1, seq2):
    """Create a hybrid sequence from two parent sequences"""
    # Find a split point at a space character
  
    spaces1 = [i for i, char in enumerate(seq1) if char == ' ']
    spaces2 = [i for i, char in enumerate(seq2) if char == ' ']
    split_point1 = random.choice(spaces1)
    split_point2 = random.choice(spaces2)
    # Combine sequences
    hybrid = seq1[:split_point1] + seq2[split_point2:]

    return hybrid


def create_block_sequence_from_motifs(motifs, config: NumbersConfig = NumbersConfig()):
    """
    Placeholder function to create sequences from motifs
    To be replaced with specific rules for motif arrangement
    """
    # The number of blocks is normaly distributed 
    num_blocks = int(np.random.normal(5.3, 1.7))
    # Less than 0 block are set to 0
    num_blocks = max(0, num_blocks)

    # Each block starts with a motif with a "pos1" in the sequence header
    # After that 1 to 6 motifs are added with "pos2" in the sequence header
    # A last motif with "pos3" in the sequence header completes the block
    # The blocks are concatenated to form the final sequence which always ends with a motif with "pos1" in the sequence header

    # Create a list to store the blocks
    blocks = []

    # Group motifs by position
    pos1_motifs = [m for m in motifs if "pos1" in m.description]
    pos2_motifs = [m for m in motifs if "pos2" in m.description]
    pos3_motifs = [m for m in motifs if "pos3" in m.description]

    for _ in range(num_blocks):
        # Start with a motif with "pos1" in the sequence header
        if pos1_motifs:
            motif1 = random.choice(pos1_motifs)
            blocks.append(str(motif1.seq))

        # Add motifs with "pos2" in the sequence header
        if pos2_motifs:
            num_motifs = max(1, int(round(np.random.normal(config.mean_motifs_per_block -2, config.std_motifs_per_block))))
            selected_motifs = random.choices(pos2_motifs, k=num_motifs)
            blocks.extend(str(m.seq) for m in selected_motifs)

        # Add a last motif with "pos3" in the sequence header
        if pos3_motifs:
            motif3 = random.choice(pos3_motifs)
            blocks.append(str(motif3.seq))

    # Add one final motif with "pos1" in the sequence header
    if pos1_motifs:
        motif4 = random.choice(pos1_motifs)
        blocks.append(str(motif4.seq))

    # Concatenate the blocks to form the final sequence
    final_sequence = ' '.join(blocks)
    return final_sequence


def create_random_sequence_from_motifs(motifs, min_motifs=1, max_motifs=30, config: NumbersConfig = NumbersConfig()):
    """
    Create a sequence by randomly concatenating motifs.
    
    Args:
        motifs: List of possible motifs to use
        min_motifs: Minimum number of motifs to include
        max_motifs: Maximum number of motifs to include
    
    Returns:
        String with space-separated motifs
    """
    # Choose random number of motifs between min and max
    num_motifs = int(np.random.normal(config.mean_motifs, config.std_motifs))
    num_motifs = max(min_motifs, min(max_motifs, num_motifs))  # Clip to min/max range
    
    # Randomly select motifs and join with spaces
    selected_motifs = random.choices(motifs, k=num_motifs)
    sequence = ' '.join(str(m.seq) for m in selected_motifs)
    
    return sequence

def translate_motifs(motif_list: List[str]) -> List[str]:
    """Translate each motif in list to amino acids"""
    
    translated = []
    for motif in motif_list:
        # Convert to Seq object and translate
        seq = Seq(motif)
        aa_seq = str(seq.translate())
        translated.append(aa_seq)
        
    return translated

def add_severe_mutations(synthetic_df, num_severe_mutations=200, mutation_probability=0.05, config: NumbersConfig = NumbersConfig()):
    """
    Add severely mutated versions of created sequences to the dataframe.
    
    Args:
        synthetic_df: DataFrame containing sequences
        mutation_fraction: Fraction of sequences to mutate severely
        mutation_probability: Probability of mutation for each position
        
    Returns:
        DataFrame with severe mutations added
    """
    # Sample fraction of sequences for severe mutations from actually observed HYPs
    orig_samples = random.choices(synthetic_df['original_sequence'], k=num_severe_mutations)

    # Create new rows with severe mutations
    severe_mutations = []
    for orig_seq in tqdm(orig_samples, desc="Generating severely mutated sequences"):
        mutated = mutate_sequence(orig_seq, mutate_probability=mutation_probability)
        
        new_row = {
            'original_sequence': orig_seq,
            'split_sequence': orig_seq.split(" "),
            # 'translated_sequence': ['X'],
            'mutated_sequence': mutated,
            'sequence_type': 'severe'
        }
        severe_mutations.append(new_row)
    
    # Add new rows to dataframe
    severe_mutations_df = pd.DataFrame(severe_mutations)
    return pd.concat([synthetic_df, severe_mutations_df], ignore_index=True)

def add_random_sequences(synthetic_df, n_full_random, config: NumbersConfig = NumbersConfig()):
    """Add fully random nucleic acid sequences to the dataframe."""
    # Pre-allocate lists to store all new data
    random_seqs = []
    
    # Generate all sequences at once
    for _ in tqdm(range(n_full_random), desc="Generating random sequences"):
        seq_len = int(random.gauss(config.random_mean_lenght, config.random_std_lenght))
        seq_len = max(0, seq_len)
        random_seq = ''.join(random.choices(['A','T','C','G'], k=seq_len))
        random_seqs.append(random_seq)
    
    # Create a single DataFrame with all new sequences at once
    new_rows = pd.DataFrame({
        'original_sequence': random_seqs,
        'split_sequence': [['X']] * n_full_random,
        'mutated_sequence': random_seqs,
        'sequence_type': ['full_random'] * n_full_random
    })
    
    # Single concatenation operation
    return pd.concat([synthetic_df, new_rows], ignore_index=True)



def generate_synthetic_dataset(
    real_seq_path,
    motifs_path,
    conserved_path,
    n_real,
    n_hybrid,
    n_block_based,
    n_random_motif_based,
    n_full_random, 
    n_severe
):
    """
    Generate a synthetic dataset with:
    - n_real sequences sampled from real sequences
    - n_hybrid hybrid sequences created from real sequences
    - n_block_based sequences constructed from motifs in blocks
    - n_random sequences constructed randomly from motifs
    - n_severe severely mutated sequences
    - n_full_random completely random sequences
    """
    
    # Load motifs
    motifs = load_motifs(motifs_path)
    synthetic_dataset = []
    sequence_types = []
    # Set up logging
    logger = logging.getLogger(__name__)
    
    # Sample real sequences
    logger.info(f"Sampling {n_real} real sequences")
    if n_real > 0:
        real_sequences = load_sequences(real_seq_path)
        real_samples = random.choices(real_sequences, k=n_real)
        synthetic_dataset.extend(real_samples)
        sequence_types.extend(['real'] * n_real)
    
    # Create hybrid sequences
    logger.info(f"Creating {n_hybrid} hybrid sequences")
    for _ in range(n_hybrid):
        seq1, seq2 = random.choices(real_sequences, k=2)
        hybrid_seq = create_hybrid_sequence(seq1, seq2)
        synthetic_dataset.append(hybrid_seq)
        sequence_types.append('hybrid')
    
    # Create block-based sequences
    logger.info(f"Creating {n_block_based} block-based sequences")
    for _ in range(n_block_based):
        block_seq = create_block_sequence_from_motifs(motifs)
        synthetic_dataset.append(block_seq)
        sequence_types.append('block_based')

    # Create random-motif-based sequences 
    logger.info(f"Creating {n_random_motif_based} random motif-based sequences")
    for _ in range(n_random_motif_based):
        random_motif_seq = create_random_sequence_from_motifs(motifs)
        synthetic_dataset.append(random_motif_seq)
        sequence_types.append('random_motif')
    
    logger.info("Creating initial dataframe")
    # Create dataframe with original sequences and types
    synthetic_df = pd.DataFrame({
        'original_sequence': synthetic_dataset,
        'sequence_type': sequence_types
    })
    
    # Add split sequences
    logger.info("Adding split sequences")
    synthetic_df['split_sequence'] = synthetic_df['original_sequence'].apply(lambda seq: seq.split(" "))
    
    # # Add translated sequences
    # synthetic_df['translated_sequence'] = synthetic_df['split_sequence'].apply(translate_motifs)
    
    # Mutate the sequences
    logger.info("Mutating sequences")
    synthetic_df['mutated_sequence'] = synthetic_df['original_sequence'].apply(mutate_sequence)

    ## Create negative examples that are not supposed to be found with a parser script
    # Add highly mutated sequences
    logger.info(f"Adding {n_severe} severely mutated sequences")
    synthetic_df = add_severe_mutations(synthetic_df, num_severe_mutations=n_severe) 

    # Add completely random sequences
    logger.info(f"Adding {n_full_random} random sequences")
    synthetic_df = add_random_sequences(synthetic_df, n_full_random)

    # Shuffle the dataframe
    logger.info("Shuffling dataframe")
    synthetic_df = synthetic_df.sample(frac=1).reset_index(drop=True)
    
    # Add conserved regions
    conserved_start, conserved_end = load_conserved(conserved_path)

    # Add conserved regions to mutated sequences
    logger.info("Adding conserved regions to sequences")
    synthetic_df['mutated_sequence'] = synthetic_df['mutated_sequence'].apply(lambda x: conserved_start + x + conserved_end)

    # Drop the original sequences as they are not needed anymore and can be obtained from the split sequences
    synthetic_df = synthetic_df.drop(columns=['original_sequence'])

    # Calculate Levenshtein distances between original and mutated sequences
    levenshtein_distances = []
    for idx, row in synthetic_df.iterrows():
        orig = ''.join(row['split_sequence'])
        mut = row['mutated_sequence'][len(conserved_start):-len(conserved_end)]
        distance = Levenshtein.distance(orig, mut)
        levenshtein_distances.append(distance)
    
    # Add Levenshtein distances as a column to the dataframe
    synthetic_df['levenshtein_distance'] = levenshtein_distances

    return synthetic_df


def mutate_sequence(sequence: str, mutate_probability = 0.0092): # The mutation rate is chosen to yield a similar rate of "flawless" reads as in the real data
    """Mutate a DNA sequence by adding insertions, deletions and substitutions"""
    # Convert sequence to list for easier mutation
    seq_list = list(sequence.replace(' ', ''))
    i = 0
    
    while i < len(seq_list):
        # Allow multiple mutations in one spot
        while random.random() < mutate_probability:
            x = random.randint(0,2)
            if x == 0:
                # Add insertions
                base = random.choice(['A','T','C','G'])
                seq_list.insert(i, base)
                i += 1
            elif x == 1:
                # Add deletions
                if len(seq_list) > 1:  # Prevent deleting entire sequence
                    seq_list.pop(i)
                    i = max(0, i-1)  # Move back one position after deletion
            else:
                # Add substitution mutations
                bases = ['A','T','C','G']
                bases.remove(seq_list[i])  # Remove current base
                seq_list[i] = random.choice(bases)
        i += 1

    return ''.join(seq_list)


def synth_main(n, n_real, n_hybrid, n_severe, n_random_motif, n_block, n_full_random, real_reads_file, motifs, conserved_file, output_dir):

    # If no numbers are provided, set the number of sequences to generate for each category to one sixth of the total number of sequences
    if sum([n_real, n_hybrid, n_severe, n_random_motif, n_block, n_full_random]) == 0:
        n_real = int(n/6)
        n_hybrid = int(n/6)
        n_severe = int(n/6)
        n_random_motif = int(n/6)
        n_block = int(n/6)
        n_full_random = int(n/6)
        
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # If the output file already exists, skip the processing
    if os.path.exists(output_dir + '/synthetic_sequences.fasta'):
        print(f"Skipping: \n{output_dir} \nOutput files already exists.")
        exit()
    
    # Generate dataset
    synthetic_sequences = generate_synthetic_dataset(
        real_seq_path=real_reads_file,
        motifs_path=motifs,
        conserved_path=conserved_file,
        n_real=n_real,
        n_hybrid=n_hybrid,
        n_block_based=n_block,
        n_random_motif_based=n_random_motif,
        n_full_random=n_full_random,
        n_severe=n_severe
    )

    # Get the length of start and end conserved regions
    conserved_start, conserved_end = load_conserved(conserved_file)
    conserved_start_len = len(conserved_start)
    conserved_end_len = len(conserved_end)

    # print the mean length of the sequences minus the conserved regions
    print(f'Mean length of sequences minus conserved regions: {np.mean([len(seq) - conserved_start_len - conserved_end_len for seq in synthetic_sequences["mutated_sequence"]])}')

    
    # Write pandas dataframe to csv
    # Generate unique IDs for each sequence
    synthetic_sequences['sequence_id'] = [f'seq_{i}' for i in range(len(synthetic_sequences))]

    # Write sequences to fasta file
    logger = logging.getLogger(__name__)
    logger.info("Writing sequences to fasta file")

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_dir + '/synthetic_sequences.fasta', 'w') as f:
        for _, row in synthetic_sequences.iterrows():
            f.write(f'>{row["sequence_id"]}\n')
            f.write(f'{row["mutated_sequence"]}\n')

    # Write metadata to csv, excluding the sequence column
    metadata_df = synthetic_sequences.drop('mutated_sequence', axis=1)
    # Remove extension from output path for metadata file
    metadata_df.to_csv(output_dir + '/synthetic_sequences_metadata.csv', index=False)

   
if __name__ == "__main__":
    synth_main()





