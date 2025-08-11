"""Create dicodon optimized coding DNA sequences"""

from . import hmm
import collections

# the universal genetic code
genetic_code = """TTT F Phe
TCT S Ser      
TAT Y Tyr      
TGT C Cys  
TTC F Phe      
TCC S Ser      
TAC Y Tyr      
TGC C Cys  
TTA L Leu      
TCA S Ser      
TAA * Ter      
TGA * Ter  
TTG L Leu 
TCG S Ser      
TAG * Ter      
TGG W Trp  
CTT L Leu      
CCT P Pro      
CAT H His      
CGT R Arg  
CTC L Leu      
CCC P Pro      
CAC H His      
CGC R Arg  
CTA L Leu      
CCA P Pro      
CAA Q Gln      
CGA R Arg  
CTG L Leu 
CCG P Pro      
CAG Q Gln      
CGG R Arg  
TT I Ile      
ACT T Thr      
AAT N Asn      
AGT S Ser  
ATC I Ile      
ACC T Thr      
AAC N Asn      
AGC S Ser  
ATA I Ile      
ACA T Thr      
AAA K Lys      
AGA R Arg  
ATG M Met
ACG T Thr      
AAG K Lys      
AGG R Arg  
GTT V Val      
GCT A Ala      
GAT D Asp      
GGT G Gly  
GTC V Val      
GCC A Ala      
GAC D Asp      
GGC G Gly  
GTA V Val      
GCA A Ala      
GAA E Glu      
GGA G Gly  
GTG V Val      
GCG A Ala      
GAG E Glu      
GGG G Gly"""

# translate the genetic code into dictionaries for easy reference
codon_to_aa_short = {}  # {tct -> S}
aa_short_to_codons = {}  # {S -> set(tct, tcc, tca, tcg, agt, agc...}
for line in genetic_code.split("\n"):
    line = line.split()
    codon = line[0].lower()
    aa_short = line[1]
    codon_to_aa_short[codon] = aa_short
    if not aa_short in aa_short_to_codons:
        aa_short_to_codons[aa_short] = set()
    aa_short_to_codons[aa_short].add(codon)


def optimize_dicodon_usage(amino_acid_sequence, dicodon_score_dict):
    """Take an amino_acid_sequence and a dict of
    {(codon, codon): score}, and produce:
    (optimized DNA sequence, [(dicodon, score)])
    """
    states = codon_to_aa_short  # a dict of {codon: Amino acid}
    transition_scores = dicodon_score_dict
    hidden_markov_model = hmm.DegenerateHMM(states, transition_scores)
    maximum_score, state_sequence = hidden_markov_model.viterbi(amino_acid_sequence)
    optimized_sequence = "".join(state_sequence)
    dicodon_plus_score = []
    for tt in range(0, len(state_sequence) - 1):
        dicodon = state_sequence[tt], state_sequence[tt + 1]
        score = dicodon_score_dict[
            dicodon
        ]  # must be in there, otherwise the viterbi should not have picked it.
        dicodon_plus_score.append((dicodon, score))
    return optimized_sequence, dicodon_plus_score


def dicodon_count_from_sequences(list_of_dna_sequences, return_errors=False):
    """Count occuring dicodons in a list of sequences.
    Non occuring dicodons are not in the output list"""
    dicodon_frequency = collections.Counter()
    if not list_of_dna_sequences:
        raise ValueError("Empty sequence passed")
    errors = []
    for sequence in list_of_dna_sequences:
        msg = None
        if len(sequence) % 3 != 0:
            msg = (
                "a sequence was not a multiple of 3 bases - not a coding sequence %s"
                % sequence
            )
        elif len(sequence) < 6:
            msg = (
                "A sequence was to short (did not contain a single dicodon): %s"
                % sequence
            )
        if msg:
            if return_errors:
                errors.append(msg)
                continue
            else:
                raise ValueError(msg)
        sequence = sequence.lower()
        for start_pos in range(0, len(sequence), 3):  # assumption: in frame sequence
            dicodon = sequence[start_pos : start_pos + 6]
            if len(dicodon) < 6:
                break  # end of sequence
            codonA = dicodon[:3]
            codonB = dicodon[3:]
            if codonA not in codon_to_aa_short:
                # continue
                raise ValueError("Unknown codon: %s" % codonA)
            if codonB not in codon_to_aa_short:
                # continue
                raise ValueError("Unknown codon: %s" % codonB)
            dicodon_frequency[codonA, codonB] += 1
    if return_errors:
        return dicodon_frequency, errors
    else:
        return dicodon_frequency


def codon_count_from_sequences(list_of_dna_sequences):
    """Count occuring codons in a list of sequences.
    Non occuring codons are not in the output list"""
    codon_frequency = collections.Counter()
    if not list_of_dna_sequences:
        raise ValueError("Empty sequence passed")
    for sequence in list_of_dna_sequences:
        if len(sequence) % 3 != 0:
            raise ValueError(
                "a sequence was not a multiple of 3 bases - not a coding sequence"
            )
        sequence = sequence.lower()
        for start_pos in range(0, len(sequence), 3):  # assumption: in frame sequence
            codon = sequence[start_pos : start_pos + 3]
            codon_frequency[codon] += 1
    return codon_frequency


def dicodon_score_dict_from_sequences(list_of_dna_sequences, return_errors=False):
    # first, count di codons.
    dicodon_counts, errors = dicodon_count_from_sequences(list_of_dna_sequences, True)
    if not return_errors:
        raise ValueError(errors)
    result = {}
    amino_acids = set(codon_to_aa_short.values())
    for firstCodon in codon_to_aa_short:  # starting at one codon
        for secondAA in amino_acids:  # we find all paths that lead to a given AA
            dicodons_for_this_transition = []
            codons_for_second = aa_short_to_codons[secondAA]
            for codonB in codons_for_second:
                dicodon = (firstCodon, codonB)
                if dicodon in dicodon_counts:  # we observed this dicodon:
                    dicodons_for_this_transition.append(
                        (dicodon, dicodon_counts[dicodon])
                    )
            # now, we have a list of observed dicodons from firstCodon to secondAA, and their frequency, we normalize it to a sum of 1.0
            total_sum = float(sum(x[1] for x in dicodons_for_this_transition))
            for dicodon, frequency in dicodons_for_this_transition:
                score = frequency / total_sum
                result[dicodon] = score
    if return_errors:
        return result, errors
    else:
        return result


def score(dna_sequence, dicodon_score_dict):
    """Look up scores for the dicodon sin dna_sequence and return a sequence
    [(dicodon, score)]
    """
    result = []
    dna_sequence = dna_sequence.lower()
    for start_pos in range(0, len(dna_sequence), 3):  # assumption: in frame sequence
        dicodon = dna_sequence[start_pos : start_pos + 6]
        if len(dicodon) < 6:
            break  # end of sequence
        key = (dicodon[:3], dicodon[3:])
        if key in dicodon_score_dict:
            score = dicodon_score_dict[key]
        else:
            score = 0
        result.append((key, score))

    return result


def translate_to_aa(dna_sequence):
    if len(dna_sequence) % 3 != 0:
        raise ValueError(
            "Not a coding DNA sequence, lenght is not divisible by 3, was %i"
            % len(dna_sequence)
        )
    aa = ""
    dna_sequence = dna_sequence.lower()
    for start in range(0, len(dna_sequence), 3):
        codon = dna_sequence[start : start + 3]
        aa += codon_to_aa_short[codon]
    return aa
