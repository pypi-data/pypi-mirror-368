# HYPeTools

This is a collection of tools for analyzing HYPe sequences.

Included tools:

- Detection of HVDs and conserved regions
- Generation of synthetic HYPe HVDs
- Parsing of HVDs to motifs
- Report generation for parsed reads
- Filtering of parsed reads
- Compaction of parsed reads

Included data:
- G. pallida HYP1 HVD markers
- G. pallida HYP1 Motifs
- G. pallida HYP1 Germline Sequences


## Tools

### HVD detection

This tool splits HYPe reads into HVDs (Hypervariable Domains) and conserved domains from FASTA files by identifying the positions of the 
specified start and end markers. It can process either a single FASTA file or a directory of FASTA files. Per default, the tool will use the HVD markers from G. pallida HYP1.


```bash
 hypetools extract-hvds "path/to/folder/or/fasta/file.fasta" --hvd-markers "path/to/hvd/markers.fasta" --start-index 2 --end-index 5
```


Options:
  --hvd-markers TEXT     FASTA file containing the HVD marker sequences
                         (default: GPallida HYP1 markers)
  --start-index INTEGER  Start index of the first read to process, e.g. --start-index 10 will skip the first 9 reads.
  --end-index INTEGER    End index of the last read to process, e.g. --end-index 90 will only process until the 90th read.




### Synthetic data generation

This tool can be used to generate synthetic HYPe sequences. You can use it to create a synthetic data set to mimick real observed reads.
The synthetic data set contains reads from different categories, the user can specify the number of sequences to generate for each category.

- real observed reads - these should be sampled from real data. Per default, the tool will use the real observed HYP1 reads from G. pallida.
- hybrid reads - created by combining two real observed HYP1 reads
- random motif-based reads - created by combining a random number of motifs. The motifs can be provided by the user. Per default, the tool will use the motifs from G. pallida. HYP1. Motifs should be provided in fasta format.
- block-based reads - created by combining a random number of motifs, but following the block arrangement of real observed HYP1 reads. To use this, the user needs to provide a file containing the motifs in a fasta format. The fasta headers should contain the position of the motif in the HYP block.

(Examples for the files the user can provide can be found in the HYPeTools/data folder.)

The reads are created and then mutated, which means indels and SNPs are introduced.
The mutation rate is on a per base pair basis. The rate is sampled from a normal distribution to resemble the mutation rate of real observed HYP1 reads.

The synthetic data set also contains:
- severely mutated sequences - sequences with a higher mutation rate
- completely random sequences - created by randomly combining bases
These are created as "negative controls", reads that can not be ambigously parsed.

The length of the sequences are sampled from a normal distribution to resemble the length of real observed HYP1 reads.
For the block-based and random motif-based sequences, this length is obtained by using the length of unique real obsereved HYP reads

The user can provide files containing:
- real observed HYP1 reads
- motifs
- short sections of conserved regions, these will be flanking the HVDs


Additionaly, a file will be created containing information about the synthetic data set - what category the reads belong to, and the motifs used to create the reads, as well as the number of mutations in the reads. 

The user can specify the number of reads to generate for each category.

```bash
hype-tools synth --n-real 100 --n-hybrid 200 --n-severe 100 --n-random-motif 10 --n-block 100 --n-full-random 100 --real-input real.fasta --motifs motifs.json --output output
```

or specify the total number of reads to generate and the input file.

```bash
hype-tools synth --n 600 --real-input real.fasta --motifs motifs.json --output output
```

Options:
  --n INTEGER               Number of reads to generate, only used if n-real,
                            n-hybrid, n-severe, n-random-motif, n-block or
                            n-full-random are not provided
  --n-real INTEGER          Number of real reads to generate
  --n-hybrid INTEGER        Number of hybrid reads to generate
  --n-severe INTEGER        Number of severe mutation reads to generate
  --n-random-motif INTEGER  Number of random motif reads to generate
  --n-block INTEGER         Number of block mutation reads to generate
  --n-full-random INTEGER   Number of fully random reads to generate
  --real-input TEXT         FASTA file containing real sequences, the motifs should be divided by spaces (default:
                            GPallida germline)
  --motifs TEXT             JSON file containing motif definitions (default:
                            GPallida motifs)
  --hvd-markers TEXT        FASTA file containing HVD marker sequences
                            (default: GPallida HYP1 markers)



### HYPe Parsing

This tool processes FASTA files by first detecting HVDs and then finding the motifs in the HVDs. The selection of possible motifs and HVD start and end markers can be provided by the user. This tool will output a table for each read containing the most likely sequence of motifs on a dna and protein level, their positions in the read and the quality of the parsing. If two or more motifs fit equally well, the tool will output all of them for one position.

Quality measures: 
- Excluded bases: Percentage of the read that is covered by the motifs
- Per Motif Alignment Score: Normalized semiglobal alignment score of the motif in this position, 1 is a perfect match
- Per Motif Quality Score: Alignment score of the best matching motif in this position, divided by the alignment score of the second best matching motif in this position. The quality score is between 1 and 2, 1 means no certainty, both the best and the second best matching motifs align equally well, 2 is high certainty. 
- Per Read Alignment Score: Average alignment score of the motifs in the read


```bash
 hypetools replace-parser /path/to/folder/or/fasta/file.fasta --hvds-file /path/to/hvd/markers.fasta --motifs-file /path/to/motifs.json --start-index 3 --end-index 6 
```

Options:
  --motifs-file TEXT     JSON file containing motif dna and protein sequences
  --hvds-file TEXT       FASTA file containing the HVD marker sequences
  --start-index INTEGER  Start index of the first read to process, e.g. --start-index 10 will skip the first 9 reads.
  --end-index INTEGER    End index of the last read to process, e.g. --end-index 90 will only process until the 90th read.


### Report Generation

With this tool, the user will be able to generate a report about about a parser output. The report will contain information about the HVDs, the motifs, and the quality of the parsing.


```bash
hypetools generate-report path/to/your_replace_parse_results.txt 
```




### Compacted Parsed Reads 

With this tool, the user is be able to generate a compacted version of the parsed reads file generated by the replace parser. This compacted version only contains the sequence header and the motifs, no quality information.


```bash
hypetools compact-output path/to/your_replace_parse_results.txt     
```

```bash
hypetools compact-output path/to/your_replace_parse_results.txt --no-protein    
```


```bash
hypetools compact-output path/to/your_replace_parse_results.txt --no-dna    
```

Options:
  --dna / --no-dna          Output DNA motifs (default: True)
  --protein / --no-protein  Output protein motifs (default: True)




### Filter Parsed Reads

With this tool, the user is able to filter the parsed reads based on the quality of the parsing. The user can filter based on the minimum alignment score, the excluded percentage, the quality score and the minimum average score.

```bash
hypetools filter-parsed /path/to/your_replace_parse_results.txt --min-align 0.8 --max-excl-pct 10.0 --min-qual 1.01 --min-avg-align 0.8
```

Options:
  --min-align FLOAT      Minimum alignment score threshold for individual motifs, (0 - 1)
  --min-avg-align FLOAT  Minimum average alignment score threshold for all motifs in a read, (0 - 1)
  --max-excl-pct FLOAT   Maximum excluded percentage threshold, percentage of bases that can be excluded from motif matches (0 - 100)
  --min-qual FLOAT       Minimum quality score threshold, indicates confidence in the motif assignment (1 - 2)

Even if no parameters are provided, the tool will always filter out empty items. E.g. reads that do not have any motifs or reads where no HVD was found.

##### Some suggested values:

Perfectionist:
- Maximum excluded percentage: 0.0
- Minimum quality score: 1.1
- Minimum average alignment score: 1.0
- Minimum alignment score: 1.0

High-quality:
- Maximum excluded percentage: 4
- Minimum quality score: 1.1
- Minimum average alignment score: 0.8

Medium-quality:
- Maximum excluded percentage: 6
- Minimum quality score: 1.01
- Minimum average alignment score: 0.95

Setting the minimum quality score to 1.01 will remove all reads with ambiguous motifs.




## Data

This package also includes data for G. pallida HYP1, which is used as default input for the tools. The user can specify their own data to use, which should be provided in the same format as the default data. Here is an overview of the formats of the data included in the package. You can find the data [here](https://github.com/Luisa3010/hype-tools/tree/main/HYPeTools/data).




### HVD markers

This is a section of dna from the conserved domain right before and after the HVD.

```fasta:HVD_markers.fasta
>start
GAAAGTGGTAAAAGACCCGGGAGC
>end
CATAAACACGGAGGTTATGACGAG
```



### Motifs

For most of the tools, the user can provide motifs in a json file. The json file should contain a dictionary with the motif as the key and the corresponding protein sequence as the value.

```json:motifs.json
{
    "TATGAGCGCGGAGGCGGA": "YERGGG",
    "TATGAGCGCGGAGGCGGG": "YERGGG",
    "TATGAACGCGGAGGCGGA": "YERGGG",
    "AGTAACCGCGGAGGCGGA": "SNRGGG",
    "AGTAACCGCGGGGGCGGA": "SNRGGG",
    "AGTAACCGCGGAGGCGGG": "SNRGGG",
    "AGTAACCGCGGGGGCGGG": "SNRGGG",
    "AGTGACCGCGGAGAC": "SDRGD",
    "AGTGACCGCGGAGAT": "SDRGD",
    ...
}
```

For the syntetic data generation tool, the motifs should be provided in a fasta file. If the user wants to generate sequences in a block format, the motifs should be provided in a fasta file where the headers contain the position of the motif in the HYP block.

```fasta:motifs.fasta
>motif1_pos1
TATGAGCGCGGAGGCGGA
>motif2_pos1
AGTGACCGCGGAGAC
>motif3_pos2
CGTGACAATAAGCGCGGA
>motif4_pos2
CGTGACGATCAGCGCGGA
>motif5_pos3
CGTGACCGCGGAGAC
>motif6_pos3
CGTGACGATCAGCGCGGA
...
```



### Germline Sequences

These are the sequences that have been observed very frequently as reads and therefore assumed to be germline alleles. They can be used to create synthetic data. They should be provided in a fasta file with spaces separating the motifs.

```fasta:germline_sequences.fasta
>GPallida_HYP1_1
TATGAGCGCGGAGGCGGA AGTGACCGCGGAGGCGGG CGTGACCGCGGAGAC ...
>GPallida_HYP1_2
TATGAGCGCGGAGGCGGA AGTGACCGCGGAGGCGGA CGTGACAATAAGCGCGGA ...
>GPallida_HYP1_3
...
```




## Future Tools 

### De-Novo Motif Detection

With this tool, the user will be able to scan a fasta file containing HYPe reads for new, unknown motifs. 
