import click
from HYPeTools.parser.replace_parser import replace_main
from HYPeTools.HVD.extract_HVDs import extract_main
from HYPeTools.synthetic.create_synthetic_hyp_reads import synth_main
from HYPeTools.parser.report import report_main
from HYPeTools.parser.filter_parse_output import filter_parsed_main
from HYPeTools.parser.compacter_parse_output import compacter_output_main
import os
import importlib.resources as resources 
from pathlib import Path




# Replace Parser Tool
@click.group()
def cli():
    """HYPeTools CLI"""

@cli.command()
@click.argument("input_path")
@click.option("--motifs-file", default=resources.files("HYPeTools") / "data/motifs/GPallida_HYP1_17_03_25.json", help="JSON file containing motif dna and protein sequences")
@click.option("--hvds-file", default=resources.files("HYPeTools") / "data/hvd_markers/GPallida_HYP1_HVD_markers.fasta", help="FASTA file containing the HVD marker sequences")
@click.option("--start-index", default=0, type=int, help="Start index of the first read to process")
@click.option("--end-index", default=-1, type=int, help="End index of the last read to process (default: -1 for all reads)")
@click.option("--help-info", is_flag=True, help="Show detailed help information about the replace parser tool")
def replace_parser(input_path, motifs_file, hvds_file, start_index, end_index, help_info):
    """Run the Replace Parser Tool
    
    Args:
        input_path: Input path to process, can be a file or a folder, if it is a folder, all fasta files in the folder will be processed
        motifs_file: Optional JSON file containing motif definitions - defaults to GPallida HYP1 Motifs
        hvds_file: Optional FASTA file containing the HVD sequences (conserved domain surrounding the HVD) - defaults to GPallida HYP1 
        start_index: Optional start index of the first read to process - defaults to 0
        end_index: Optional end index of the last read to process - defaults to all reads
    """
    if help_info:
        click.echo("""
            Replace Parser Tool Help:
            ------------------------
            This tool processes FASTA files by replacing specific motifs with HVD sequences.

            Required Arguments:
            motifs_file  - JSON file containing motif definitions
                            Format: {"motif1": "sequence1", "motif2": "sequence2", ...}
            hvds_file    - FASTA file containing HVD sequences to insert
            input_path   - Input path to process, can be a file or a folder, if it is a folder, all fasta files in the folder will be processed

            Example Usage:
            hypetools replace-parser motifs.json hvds.fasta input.fasta
        """)




    

   



    if not os.path.exists(input_path):
        click.echo(f"Error: Input file '{input_path}' does not exist.")
        return
    if not os.path.exists(motifs_file):
        click.echo(f"Error: Motifs file '{motifs_file}' does not exist.")
        return
    if not os.path.exists(hvds_file):
        click.echo(f"Error: HVDs file '{hvds_file}' does not exist.")
        return
    
    if end_index == -1:
        end_index = float('inf')
    
    replace_main(motifs_file, hvds_file, input_path, start_index, end_index)

@cli.command()
@click.argument("input_path")
@click.option("--hvd-markers", default=resources.files("HYPeTools") / "data/hvd_markers/GPallida_HYP1_HVD_markers.fasta",
              help="FASTA file containing the HVD marker sequences (default: GPallida HYP1 markers)")
@click.option("--start-index", default=0, type=int, help="Start index of the first read to process")
@click.option("--end-index", default=-1, type=int, help="End index of the last read to process (-1 for all reads)")
@click.option("--help-info", is_flag=True, help="Show detailed help information about the extract hvds tool")
def extract_hvds(input_path, hvd_markers, start_index, end_index, help_info):
    """Extract HVDs from input sequences
    
    Args:
        input_path: Input path to process, can be a file or a folder, if it is a folder, all fasta files in the folder will be processed
        hvd_markers: Optional FASTA file containing HVD marker sequences
        start_index: Optional start index of the first read to process - defaults to 0
        end_index: Optional end index of the last read to process - defaults to all reads
    """

    if help_info:
        click.echo("""
            Extract HVDs Tool Help:
            ------------------------
            This tool splits HYPe reads into HVDs (Hypervariable Domains) and conserved domains from FASTA files by identifying the positions of the 
            specified start and end markers. It can process either a single FASTA file or a directory of FASTA files.

            Required Arguments:
            input_path - Input path to process, can be a file or a folder, if it is a folder, all fasta files in the folder will be processed
            hvd_markers - FASTA file containing HVD marker sequences (conserved domain flanking the HVD)

            Example Usage:
            hypetools extract-hvds input.fasta hvd_markers.fasta
        """)

    if not os.path.exists(input_path):
        click.echo(f"Error: Input file '{input_path}' does not exist.")
        return
    if not os.path.exists(hvd_markers):
        click.echo(f"Error: HVDs file '{hvd_markers}' does not exist.")
        return
    
    if end_index == -1:
        end_index = float('inf')

    extract_main(input_path, hvd_markers, start_index, end_index)


@cli.command()
@click.argument("output_dir")
@click.option("--n", default=600, help="Number of reads to generate, only used if n-real, n-hybrid, n-severe, n-random-motif, n-block or n-full-random are not provided")
@click.option("--n-real", default=0, help="Number of real reads to generate")
@click.option("--n-hybrid", default=0, help="Number of hybrid reads to generate")
@click.option("--n-severe", default=0, help="Number of severe mutation reads to generate")
@click.option("--n-random-motif", default=0, help="Number of random motif reads to generate")
@click.option("--n-block", default=0, help="Number of block mutation reads to generate")
@click.option("--n-full-random", default=0, help="Number of fully random reads to generate")
@click.option("--real-input", default=resources.files("HYPeTools") / "data/germline/GPallida_HYP1_top_seqs_dna_17_03_2025.fasta", 
              help="FASTA file containing real sequences (default: GPallida germline)")
@click.option("--motifs", default=resources.files("HYPeTools") / "data/motifs/GPallida_HYP1_motifs_17_03_synthetic_base.fasta",
              help="JSON file containing motif definitions (default: GPallida motifs)")
@click.option("--hvd-markers", default=resources.files("HYPeTools") / "data/hvd_markers/GPallida_HYP1_HVD_markers.fasta",
              help="FASTA file containing HVD marker sequences (default: GPallida HYP1 markers)")
@click.option("--help-info", is_flag=True, help="Show detailed help information about the create synth reads tool")
def create_synth_reads(n, n_real, n_hybrid, n_severe, n_random_motif, 
                      n_block, n_full_random, real_input, motifs, hvd_markers, output_dir, help_info):
    
    """Create Synthetic HYP Reads
    
    Args:
    
        n: Total number of reads - only used if n-real, n-hybrid, n-severe, n-random-motif, n-block or n-full-random are not provided
        n_real: Number of real reads
        n_hybrid: Number of hybrid reads
        n_severe: Number of severe mutation reads
        n_random_motif: Number of random motif reads
        n_block: Number of block mutation reads
        n_full_random: Number of fully random reads
        real_input: Input file containing real sequences
        motifs: JSON file containing motif definitions
        hvd_markers: FASTA file containing HVD marker sequences
        output_dir: Output directory
    """

    if help_info:
        click.echo("""
            Create Synthetic HYP Reads Tool Help:
            -------------------------------------
            This tool creates synthetic HYP reads.

            Arguments:
            n - Total number of reads, only used if n-real, n-hybrid, n-severe, n-random-motif, n-block or n-full-random are not provided
            n_real - Number of real reads
            n_hybrid - Number of hybrid reads
            n_severe - Number of severe mutation reads
            n_random_motif - Number of random motif reads
            n_block - Number of block mutation reads
            n_full_random - Number of fully random reads
            real_input - Input file containing real sequences
            motifs - JSON file containing motif definitions
            hvd_markers - FASTA file containing HVD marker sequences
            output_dir - Output directory
                   
            Defaults to G. Pallida HYP1 reads, motifs and markers.
        """)
                   
    synth_main(n=n, n_real=n_real, n_hybrid=n_hybrid, n_severe=n_severe,
               n_random_motif=n_random_motif, n_block=n_block, n_full_random=n_full_random,
               real_reads_file=real_input, motifs=motifs, conserved_file=hvd_markers, output_dir=output_dir)

@cli.command()
@click.argument("parser_output_file")
@click.option("--help-info", is_flag=True, help="Show detailed help information about the generate report tool")
def generate_report(parser_output_file, help_info):
    """Generate a report from parser output
    
    Args:
        parser_output_file: Path to the parser output file
    """
    if help_info:
        click.echo("""
            Generate Report Tool Help:
            ------------------------
            This tool generates a statistical report from parser output, including:
            - Statistical summary of scores and excluded percentages
            - Count of empty and non-empty reads
            - Quality distribution of reads (low, medium, high, and perfect quality)

            Required Arguments:
            parser_output_file - Path to the parser output file

            Example Usage:
            hypetools generate-report parser_output.pkl
        """)

    if not os.path.exists(parser_output_file):
        click.echo(f"Error: Parser output file '{parser_output_file}' does not exist.")
        return
    
    report_main(parser_output_file)

@cli.command()
@click.argument("parser_output_file")
@click.option("--min-align", default=0.0, type=float, help="Minimum alignment score threshold 0 to 1")
@click.option("--min-avg-align", default=0.0, type=float, help="Minimum average alignment score threshold 0 to 1")
@click.option("--max-excl-pct", default=100.0, type=float, help="Maximum excluded percentage threshold 0 to 100")
@click.option("--min-qual", default=1.0, type=float, help="Minimum quality score threshold 1 to 2")
@click.option("--help-info", is_flag=True, help="Show detailed help information about the filter tool")
def filter_parsed(parser_output_file, min_align, min_avg_align, max_excl_pct, min_qual, help_info):
    """Filter parsed reads based on quality metrics
    
    Args:
        parser_output_file: Path to the parser output file
        min_align: Minimum alignment score threshold (0.0 to 1.0)
        min_avg_align: Minimum average score threshold (0.0 to 1.0)
        max_excl_pct: Maximum excluded percentage threshold (0.0 to 100.0)
        min_qual: Minimum quality score threshold (1.0 to 2.0)
    """
    if help_info:
        click.echo("""
            Filter Parsed Reads Tool Help:
            -----------------------------
            This tool filters parsed reads based on various quality metrics:
            - Minimum alignment score: Threshold for individual motif alignments
            - Minimum average score: Threshold for average alignment score across all motifs
            - Maximum excluded percentage: Maximum allowed percentage of excluded regions
            - Minimum quality score: Threshold for quality scores

            Required Arguments:
            parser_output_file - Path to the parser output file

            Example Usage:
            hypetools filter-parsed parser_output.fasta --min-alignment-score 0.7 
            Per default, the tool will filter out reads where no motfs have been found.
        """)

    if not os.path.exists(parser_output_file):
        click.echo(f"Error: Parser output file '{parser_output_file}' does not exist.")
        return
    
    filter_parsed_main(parser_output_file, min_align, min_avg_align, max_excl_pct, min_qual)

@cli.command()
@click.argument("parser_output_file")
@click.option("--dna/--no-dna", default=True, help="Output DNA motifs (default: True)")
@click.option("--protein/--no-protein", default=True, help="Output protein motifs (default: True)")
@click.option("--help-info", is_flag=True, help="Show detailed help information about the compacter tool")
def compact_output(parser_output_file, dna, protein, help_info):
    """Create compact representation of parsed reads
    
    Args:
        parser_output_file: Path to the parser output file
        dna: Whether to output DNA motifs
        protein: Whether to output protein motifs
    """
    if help_info:
        click.echo("""
            Compact Output Tool Help:
            ------------------------
            This tool creates a compact representation of parsed reads by joining motifs with spaces.
            It can output both DNA and protein motif sequences in FASTA format.

            Required Arguments:
            parser_output_file - Path to the parser output file

            Options:
            --dna/--no-dna - Include/exclude DNA motifs output (default: include)
            --protein/--no-protein - Include/exclude protein motifs output (default: include)

            Example Usage:
            hypetools compact-output parser_output.fasta --dna --no-protein
        """)

    if not os.path.exists(parser_output_file):
        click.echo(f"Error: Parser output file '{parser_output_file}' does not exist.")
        return
    
    compacter_output_main(parser_output_file, dna, protein)

if __name__ == "__main__":
    cli()



# TODO:  
# Test the tools
