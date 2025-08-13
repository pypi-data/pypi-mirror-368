import os
import json
from HYPeTools.utils import translate
from Levenshtein import distance as levenshtein_distance
import pandas as pd

def create_folder(path):
    # Create folder if it doesnt exist yet 

    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print(f"Error creating folder: {e}")
        raise


def create_output_filename(fasta_file, start_index=0, end_index=float('inf')):
    # Create output file - use only the filename, not the full path
    filename = os.path.basename(fasta_file)
    output_folder = os.path.dirname(fasta_file)
    # Add start and end indices to filename if not default values
    # Create extension for output files
    ext = ""
    if start_index != 0 and end_index == float('inf'):
        ext = "_" + str(start_index)
    if end_index != float('inf'):
        ext = "_" + str(start_index) + "to" + str(end_index)
    return os.path.join(output_folder, f'{".".join(filename.split(".")[:-1])}_replace_parse_result{ext}.txt')




def read_motifs(path):
    # Read motifs from a json file
    with open(path, 'r') as f:
        motifs = json.load(f)
    return motifs



def translate_motif(motif, motifs_table):
    # Translate a motif into amino acids
    
    if motif in motifs_table:
        return motifs_table[motif]
    else:

        variants = translate(motif)
        # Get the frame that has the smallest levenshtein distance to an existing motif from the table
        min_distance = float('inf')
        best_frames = []
        for variant in variants:
            for frame in variant:
                for motif in motifs_table.values():
                    distance = levenshtein_distance(frame, motif)
                    if distance <= min_distance:
                        min_distance = distance
                        best_frames.append(frame)


        # If all the best frames are identical, return the first one
        if all(frame == best_frames[0] for frame in best_frames):
            return best_frames[0]
        
        # Get unique frames by converting each to tuple, using set, then back to list
        unique_frames = list(set(tuple(frame) if isinstance(frame, list) else frame for frame in best_frames))
        return unique_frames




class ParserResult:
    
    def __init__(self, header, read, motifs_df, avg_score, excluded_pct):
        self.header = header
        self.read = read
        self.motifs_df = motifs_df
        self.avg_score = avg_score
        self.excluded_pct = excluded_pct

    def __str__(self):
        """
        Returns a string representation of the parser result in the same format as the input file.
        """
        if self.read is None:
            return f"{self.header}\nNo HVD found\n-\nExcluded Bases: {self.excluded_pct:.3f}%, Average alignment score: {self.avg_score:.6f}"
        
        output = [
            self.header,
            self.read,
        ]
        
        # Add motifs dataframe string representation
        output.append(str(self.motifs_df))
        # Add metrics line
        output.append(f"Excluded Bases: {self.excluded_pct:.3f}%, Average alignment score: {self.avg_score:.6f}")
        
        return "\n".join(output)


def load_parser_output(path):
    """
    Load parser output file and return an iterator of results.
    Each iteration returns an object containing:
    - header: sequence header (e.g. ">seq_0") 
    - read: the sequence read (or None if no HVD found)
    - motifs_df: pandas DataFrame of found motifs (or None if no HVD found)
    - avg_score: average alignment score
    - excluded_pct: percentage of excluded bases
    """

    with open(path, 'r') as f:
        while True:
            # Read header
            header = f.readline().strip()
            if not header:  # End of file
                break
                
            # Read sequence/result
            line = f.readline().strip()
            if line == "No HVD found":
                # Skip the "-" line
                f.readline()
                # Read metrics line
                metrics = f.readline().strip()
                excluded_pct = float(metrics.split("Excluded Bases: ")[1].split("%")[0])
                avg_score = float(metrics.split("Average alignment score: ")[1])
                
                yield ParserResult(header, None, None, avg_score, excluded_pct)
                
            else:
                read = line

                # Skip table header
                f.readline()
                # Read the data as pd df
                df_rows = []
                while True:
                    line = f.readline().strip()
                    # Check if line matches expected format with multiple whitespace-separated fields
                    if line.startswith("Excluded Bases"):
                        break
                    df_rows.append(line)
                
                # Create DataFrame from rows
                df_rows = [row.replace(', ', '*').split() for row in df_rows]
                motifs_df = pd.DataFrame(df_rows, columns=['id','start_pos', 'end_pos', 'original_dna', 'motif', 'alignment_score', 'amino_acid', 'quality_score'])
                motifs_df['amino_acid'] = motifs_df['amino_acid'].str.replace('*', ', ')

                # Convert numeric columns to appropriate types
                motifs_df['start_pos'] = motifs_df['start_pos'].astype(int)
                motifs_df['end_pos'] = motifs_df['end_pos'].astype(int) 
                motifs_df['alignment_score'] = motifs_df['alignment_score'].astype(float)
                
                # Get excluded percentage from metrics line
                metrics = line
                excluded_pct =  float(line.split("Excluded Bases: ")[1].split('%')[0])
                avg_score = float(metrics.split("Average alignment score: ")[1])
                yield ParserResult(header, read, motifs_df, avg_score, excluded_pct)



def write_results(output_file, header, read, replaced_motifs, coverage, average_alignment_score):\
    # Create output file if it doesn't exist
    if not os.path.exists(output_file):
        with open(output_file, 'w') as f:
            pass
    with open(output_file, 'a') as f:
        f.write(f"{header}\n")
        if replaced_motifs.empty:
            f.write("No HVD found\n-\n")
        else:
            f.write(f"{read}\n")
            # Use to_string() to write full DataFrame content without truncation
            f.write(f"{replaced_motifs.to_string(index=False)}\n")
        f.write(f"Excluded Bases: {((1 - coverage) * 100):.3f}%, Average alignment score: {average_alignment_score:.6f}\n")



