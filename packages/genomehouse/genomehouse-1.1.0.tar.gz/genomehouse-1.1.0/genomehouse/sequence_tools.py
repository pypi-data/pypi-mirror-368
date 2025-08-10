"""
Sequence Analysis Tools for DNA, RNA, and Protein Manipulation
"""
import re
from typing import List, Optional

def reverse_complement(seq: str, seq_type: str = "DNA") -> str:
    """Return the reverse complement of a DNA or RNA sequence."""
    complement = {
        "A": "T" if seq_type == "DNA" else "U",
        "T": "A",
        "U": "A",
        "G": "C",
        "C": "G",
        "N": "N"
    }
    return "".join(complement.get(base.upper(), base) for base in reversed(seq))

def find_motif(seq: str, motif: str) -> List[int]:
    """Return all start positions (0-based) where motif occurs in sequence."""
    return [m.start() for m in re.finditer(f"(?={motif})", seq)]

def gc_content(seq: str) -> float:
    """Calculate GC content percentage of a sequence."""
    gc = sum(1 for base in seq.upper() if base in ["G", "C"])
    return (gc / len(seq)) * 100 if seq else 0.0

def translate(seq: str, frame: int = 1) -> str:
    """Translate DNA sequence to protein (single-letter code). Frame is 1-based."""
    codon_table = {
        "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
        "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
        "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
        "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
        "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
        "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
        "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
        "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
        "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
        "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
        "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
        "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
        "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
        "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
        "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
        "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G"
    }
    seq = seq.upper().replace("U", "T")
    prot = []
    for i in range(frame - 1, len(seq) - 2, 3):
        codon = seq[i:i+3]
        prot.append(codon_table.get(codon, "X"))
    return "".join(prot)
