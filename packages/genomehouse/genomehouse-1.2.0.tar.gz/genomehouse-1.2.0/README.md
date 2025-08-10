# GenomeHouse

GenomeHouse is a modular, user-friendly Python toolkit for bioinformatics and genomics research. It provides tools for sequence analysis, genomic data parsing, machine learning, visualization, and more—all under one roof.

## Features
- Sequence analysis: reverse complement, motif search, GC content, translation
- Genomic data parsing: FASTA, FASTQ, VCF, GFF/GTF
- Machine learning pipelines for biological data
- Publication-quality data visualization
- Statistical analysis tools
- Extensible and user-friendly API

## Installation
```bash
pip install genomehouse
```

## Quick Start
```python
from genomehouse import sequence_tools, genomic_parsers
seq = "ATGCGTAC"
print(sequence_tools.gc_content(seq))
for header, seq in genomic_parsers.parse_fasta("example.fasta"):
	print(header, seq)
```

## CLI Usage
```bash
genomehouse-cli parse-fasta data/sample.fasta
genomehouse-cli gc-content ATGCGTAC
```

## Documentation
See the `docs/` folder for full API documentation and usage examples.

## License
[License](LICENSE)

## Source Code
[GitHub Repository](https://github.com/GenomeHouse/GenomeHouse-1.1)