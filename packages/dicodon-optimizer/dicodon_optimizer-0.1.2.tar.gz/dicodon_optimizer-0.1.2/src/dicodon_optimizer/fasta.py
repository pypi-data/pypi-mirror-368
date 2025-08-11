import re

def parse_fasta_to_dict(fasta):
    """Parse a fasta file into a dictionary of name -> sequence"""
    if not fasta.startswith('>'):
        raise ValueError("Input did not start with '>', not  a valid Fasta file")
    result = {}
    for block in fasta.split(">"):
        block = block.strip()
        if block:
            new_line_pos = block.find('\n')
            name = block[:new_line_pos]
            sequence_plus_whitespace = block[new_line_pos:]
            sequence = re.sub('\s+','', sequence_plus_whitespace).lower()
            result[name] = sequence
    return result

