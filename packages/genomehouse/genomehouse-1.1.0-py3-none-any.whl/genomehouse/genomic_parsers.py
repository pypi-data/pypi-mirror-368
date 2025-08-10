"""
Genomic Data Parsers for FASTA, FASTQ, VCF, and GFF/GTF
"""
from typing import List, Dict, Any, Tuple, Generator
import re

def parse_fasta(file_path: str) -> Generator[Tuple[str, str], None, None]:
    """Yield (header, sequence) tuples from a FASTA file."""
    header = None
    seq = []
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if header:
                    yield (header, "".join(seq))
                header = line[1:]
                seq = []
            else:
                seq.append(line)
        if header:
            yield (header, "".join(seq))

def parse_fastq(file_path: str) -> Generator[Dict[str, str], None, None]:
    """Yield dicts with 'id', 'seq', 'plus', 'qual' from a FASTQ file."""
    with open(file_path) as f:
        while True:
            id_line = f.readline()
            if not id_line:
                break
            seq_line = f.readline()
            plus_line = f.readline()
            qual_line = f.readline()
            if not (seq_line and plus_line and qual_line):
                break
            yield {
                'id': id_line.strip()[1:],
                'seq': seq_line.strip(),
                'plus': plus_line.strip(),
                'qual': qual_line.strip()
            }

def parse_vcf(file_path: str) -> Generator[Dict[str, Any], None, None]:
    """Yield dicts for each VCF record."""
    with open(file_path) as f:
        for line in f:
            if line.startswith('#'):
                continue
            fields = line.strip().split('\t')
            if len(fields) < 8:
                continue
            yield {
                'CHROM': fields[0],
                'POS': fields[1],
                'ID': fields[2],
                'REF': fields[3],
                'ALT': fields[4],
                'QUAL': fields[5],
                'FILTER': fields[6],
                'INFO': fields[7]
            }

def parse_gff(file_path: str) -> Generator[Dict[str, Any], None, None]:
    """Yield dicts for each GFF/GTF record."""
    with open(file_path) as f:
        for line in f:
            if line.startswith('#'):
                continue
            fields = line.strip().split('\t')
            if len(fields) < 9:
                continue
            yield {
                'seqid': fields[0],
                'source': fields[1],
                'type': fields[2],
                'start': fields[3],
                'end': fields[4],
                'score': fields[5],
                'strand': fields[6],
                'phase': fields[7],
                'attributes': fields[8]
            }
