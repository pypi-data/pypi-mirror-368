import sys

__version__ = "0.1"
from .dicodon_optimization import (
    optimize_dicodon_usage,
    dicodon_count_from_sequences,
    codon_count_from_sequences,
    dicodon_score_dict_from_sequences,
    score,
    translate_to_aa,
)
from .fasta import parse_fasta_to_dict
