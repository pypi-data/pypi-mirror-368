import os
from typing import List


    # Consensus table: Nucleotide symbol -> Component nucleotides
consensus_table = {
    'A': ['A'],
    'C': ['C'],
    'G': ['G'], 
    'T': ['T'],
    'U': ['U'],
    'R': ['G', 'A'],
    'Y': ['C', 'T'],
    'K': ['G', 'T'],
    'M': ['A', 'C'],
    'S': ['G', 'C'],
    'W': ['A', 'T'],
    'B': ['G', 'T', 'C'],
    'D': ['G', 'A', 'T'],
    'H': ['A', 'C', 'T'],
    'V': ['G', 'C', 'A'],
    'N': ['A', 'G', 'C', 'T']
}


codon_table = {
        'ATA': 'I', 'ATC': 'I', 'ATT': 'I', 'ATG': 'M',
        'ACA': 'T', 'ACC': 'T', 'ACG': 'T', 'ACT': 'T',
        'AAC': 'N', 'AAT': 'N', 'AAA': 'K', 'AAG': 'K',
        'AGC': 'S', 'AGT': 'S', 'AGA': 'R', 'AGG': 'R',
        'CTA': 'L', 'CTC': 'L', 'CTG': 'L', 'CTT': 'L',
        'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCT': 'P',
        'CAC': 'H', 'CAT': 'H', 'CAA': 'Q', 'CAG': 'Q',
        'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGT': 'R',
        'GTA': 'V', 'GTC': 'V', 'GTG': 'V', 'GTT': 'V',
        'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCT': 'A',
        'GAC': 'D', 'GAT': 'D', 'GAA': 'E', 'GAG': 'E',
        'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGT': 'G',
        'TCA': 'S', 'TCC': 'S', 'TCG': 'S', 'TCT': 'S',
        'TTC': 'F', 'TTT': 'F', 'TTA': 'L', 'TTG': 'L',
        'TAC': 'Y', 'TAT': 'Y', 'TAA': '_', 'TAG': '_',
        'TGC': 'C', 'TGT': 'C', 'TGA': '_', 'TGG': 'W',
}


def find_fastas(path):
    # If path is a file, return it, if it is a folder, return a list of all fasta files in the folder
    if os.path.isfile(path):
        return [path]
    elif os.path.isdir(path):
        return [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.fasta') or f.endswith('.fa')]
    else:
        raise ValueError(f"Invalid path: {path}")


def read_fasta(path):
    # Read a fasta file as iterator, supporting multiline sequences
    header = None
    seq_lines = []
    with open(path, 'r') as f:
        for line in f:
            line = line.rstrip()
            if line.startswith('>'):
                if header is not None:
                    yield header, ''.join(seq_lines)
                header = line.strip()
                seq_lines = []
            else:
                seq_lines.append(line.strip())
        if header is not None:
            yield header, ''.join(seq_lines)


def dumb_consensus(dna_sequences: List[str]):    
    """Get the consensus sequence from a list of DNA sequences"""

    # Check if all sequences have the same length
    if not all(len(seq) == len(dna_sequences[0]) for seq in dna_sequences):
        raise ValueError("All DNA sequences must have the same length")

    consensus = ""
    seq_length = len(dna_sequences[0])

    # Go through each position
    for i in range(seq_length):
        # Get all nucleotides at this position
        nucleotides = [seq[i] for seq in dna_sequences]
        
        # Find consensus symbol that matches all nucleotides
        consensus_symbol = None
        for symbol, components in consensus_table.items():
            if all(nuc in components for nuc in nucleotides):
                consensus_symbol = symbol
                break
                
        if consensus_symbol is None:
            consensus_symbol = 'N'  # Default to N if no match found
            
        consensus += consensus_symbol

    return consensus
    


def disambiguate_sequences(seq):

    if not all(nuc in ['A', 'T', 'C', 'G'] for nuc in seq):
    # Get all the possible sequences using the consensus table
        possible_sequences = []
        for nuc in seq:
            if len(consensus_table[nuc]) > 1:
                for component in consensus_table[nuc]:
                    possible_sequences.extend(disambiguate_sequences(seq.replace(nuc, component)))
    
    else:
        possible_sequences = [seq]

    return possible_sequences

def translate(seq):
    # include finding the start codon
    seq = seq.upper()

    # Check if the sequence consists entirely of A, T, C, G and if it doesn't add the possible variants
    possible_sequences = disambiguate_sequences(seq)

    # Translate all possible sequences




    frames = []
    for seq in possible_sequences:
        frame1 = ""
        frame2 = ""
        frame3 = ""
        # Translate frame 1 (starting at position 0)
        for i in range(0, len(seq)-2, 3):
            codon = seq[i:i+3]
            if len(codon) == 3:
                frame1 += codon_table[codon]

        # Translate frame 2 (starting at position 1) 
        for i in range(1, len(seq)-2, 3):
            codon = seq[i:i+3]
            if len(codon) == 3:
                frame2 += codon_table[codon]
        
        # Translate frame 3 (starting at position 2)
        for i in range(2, len(seq)-2, 3):
            codon = seq[i:i+3]
            if len(codon) == 3:
                frame3 += codon_table[codon]

        frames.append([frame1, frame2, frame3])

    return frames

    


