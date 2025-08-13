import pandas as pd
from .utils import load_parser_output, write_results
import os

def filter_parsed(parser_output_path, min_alignment_score=0.7, min_avg_score=0.95, max_excluded_pct=0.05, min_quality_score=1.1):

    # Load parser output
    parser_output = load_parser_output(parser_output_path)

    filtered_output_path = os.path.splitext(parser_output_path)[0] + '_filtered.txt'
    
    print(f"Writing filtered reads to: \n{filtered_output_path}")
    # Check if the file already exists
    if os.path.exists(filtered_output_path):
        print(f"Skipping: \n{parser_output_path} \nOutput file already exists.")
        return

    filtered_output = []
    for result in parser_output:
        data = {
        'header': result.header,
        'read': result.read,
        'avg_score': result.avg_score,
            'motifs_df': result.motifs_df,
            'excluded_pct': result.excluded_pct
        }

        # Filter reads based on score and excluded percentage
        if result.avg_score >= float(min_avg_score) \
            and result.excluded_pct <= float(max_excluded_pct) \
            and result.motifs_df['quality_score'].apply(float).min() >= float(min_quality_score) \
            and result.motifs_df['alignment_score'].apply(float).min() >= float(min_alignment_score):

            # Write the filtered reads to a new file
            write_results(filtered_output_path, result.header, result.read, result.motifs_df, (100 - result.excluded_pct)/100, result.avg_score)

def filter_parsed_main(parser_output_path, min_alignment_score=0.7, min_avg_score=0.95, max_excluded_pct=0.05, min_quality_score=1.1):

    filter_parsed(parser_output_path, min_alignment_score, min_avg_score, max_excluded_pct, min_quality_score)