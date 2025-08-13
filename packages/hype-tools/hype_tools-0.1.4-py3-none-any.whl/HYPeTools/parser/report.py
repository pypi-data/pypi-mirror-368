from .utils import load_parser_output
import pandas as pd
from collections import Counter

def generate_report(parser_output_path):

    # Load parser output
    parser_output = load_parser_output(parser_output_path)

    # Convert parser results to DataFrame
    data = [{
        'read': result.read,
        'avg_score': result.avg_score,
        'motifs_df': result.motifs_df,
        'excluded_pct': result.excluded_pct
    } for result in parser_output]
    
    df = pd.DataFrame(data)
    
    # Extract motifs from motifs_df and join them
    hvds = df['motifs_df'].apply(lambda x: ' '.join(x['motif'].tolist()) if not x is None else '').tolist()
    
    # Count motif occurrences
    all_hvds = []
    for hvd_str in hvds:
        if hvd_str:  # Skip empty strings
            all_hvds.append(hvd_str)
            
    hvd_counts = Counter(all_hvds)
    
    print("\nTop 10 most frequent HVDs:")
    for hvd, count in hvd_counts.most_common(10):
        print(f"{hvd}: {count}")    
    
    # Count empty reads
    empty_reads = df['read'].apply(lambda x: not bool(x)).sum()
    print(f"\nMissing reads:\t\t {empty_reads}")

    # Not empty reads
    not_empty_reads = df['read'].apply(lambda x: bool(x)).sum()
    print(f"Not missing reads:\t {not_empty_reads}\n")

    # Filter out empty reads
    df = df[df['read'].apply(lambda x: bool(x))]

    # Get number of reads with low quality
    low_quality_reads = df[(df['avg_score'] < 0.92) & (df['excluded_pct'] > 0.05)].shape[0]
    print(f"Low quality reads:\t {low_quality_reads}")

    # Get number of reads with medium quality
    low_medium_quality_reads = df[(df['avg_score'] < 0.98) | (df['excluded_pct'] > 0.04)].shape[0]
    print(f"Medium quality reads:\t {low_medium_quality_reads - low_quality_reads}")
    
    # Get number of reads with perfect quality
    perfect_quality_reads = df[(df['avg_score'] == 1) & (df['excluded_pct'] == 0.00)].shape[0]

    # Get number of reads with high quality
    high_quality_reads = df[(df['avg_score'] > 0.98) & (df['excluded_pct'] < 0.04)].shape[0]
    print(f"High quality reads:\t {high_quality_reads - perfect_quality_reads}")
    
    print(f"Perfect quality reads:\t {perfect_quality_reads}")
    

    # Get statistical description of numerical columns
    print("\nStatistical Summary:")
    print(df[['avg_score', 'excluded_pct']].describe())

    
    

def report_main(parser_output_path):
    
    generate_report(parser_output_path)