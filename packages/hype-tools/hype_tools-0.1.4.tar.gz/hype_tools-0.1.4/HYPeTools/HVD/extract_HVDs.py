#!/usr/bin/env python3

"""
This script splits HYPe reads into HVDs (Hypervariable Domains) and conserved domains from FASTA files by identifying the positions of the 
specified start and end markers. It can process either a single FASTA file or a directory of FASTA files.


"""
import os
import argparse
from tqdm import tqdm
from .utils import extract_hvd_from_read
from ..utils import read_fasta

def process_fasta_file(input_path, output_path, start, end, start_index, end_index):

    # Create extension for output files
    ext = ""
    if start_index != 0 and end_index == float('inf'):
        ext = "_" + str(start_index)
    if end_index != float('inf'):
        ext = "_" + str(start_index) + "to" + str(end_index)

    hvd_outfile = output_path + "_hvd" + ext 
    c1_outfile = output_path + "_c1" + ext 
    c2_outfile = output_path + "_c2" + ext 

    print("Writing to files:")
    print(hvd_outfile)
    print(c1_outfile)
    print(c2_outfile)

    # If any of the output files already exist, skip the processing
    if os.path.exists(hvd_outfile) or os.path.exists(c1_outfile) or os.path.exists(c2_outfile):
        print(f"Skipping: \n{input_path} \nAt least one of the output files already exists.")
        return

    # Open input and output files
    with open(input_path, 'r') as infile, open(hvd_outfile, 'w') as hvd_outfile, \
        open(c1_outfile, 'w') as c1_outfile, open(c2_outfile, 'w') as c2_outfile:
        for i, (header, sequence) in enumerate(read_fasta(input_path)):

            # Skip reads before start_index
            if i < start_index:
                continue
            # Skip reads after end_index
            if i > end_index:
                break

            # Process the read to extract HVD
            hvd, c1, c2 = extract_hvd_from_read(sequence, start, end)
            # Write header and HVD sequence
            hvd_outfile.write(f"{header}\n")
            hvd_outfile.write(f"{hvd}\n")
            c1_outfile.write(f"{header}\n")
            c1_outfile.write(f"{c1}\n")
            c2_outfile.write(f"{header}\n")
            c2_outfile.write(f"{c2}\n")

def extract_hvds(input_path, hvd_markers, start_index, end_index):
    """Extract HVDs from either a single file or directory of files"""

    # Read hvd_markers file
    hvd_markers = read_fasta(hvd_markers)
    start, end = [h[1] for h in hvd_markers]
    
    if os.path.isfile(input_path):
        # Process single file
        output_path = os.path.splitext(input_path)[0]
        process_fasta_file(input_path, output_path, start, end, start_index, end_index)
        
    elif os.path.isdir(input_path):
        # Process directory
        files = [f for f in os.listdir(input_path) 
                if os.path.isfile(os.path.join(input_path, f)) and f.endswith('.fasta')]
        
        output_folder = input_path + "_output"
        os.makedirs(output_folder, exist_ok=True)
        
        for filename in tqdm(files, desc="Processing files"):
            input_file = os.path.join(input_path, filename)
            output_file = os.path.join(output_folder,os.path.splitext(filename)[0])
            process_fasta_file(input_file, output_file, start, end, start_index, end_index)


def extract_main(input_path, hvd_markers, start_index, end_index):
   
    extract_hvds(input_path, hvd_markers, start_index, end_index)
