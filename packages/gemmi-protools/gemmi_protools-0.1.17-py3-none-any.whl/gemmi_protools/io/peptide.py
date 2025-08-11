"""
@Author: Luo Jiejian
"""
from copy import deepcopy

from Bio.PDB.Polypeptide import nucleic_letters_3to1_extended, protein_letters_3to1_extended


def strip_key_val(inputs):
    outputs = dict()
    for key, val in inputs.items():
        outputs[key.strip()] = val.strip()
    return outputs


def __nucleic_3to1_mapper():
    mapper = deepcopy(nucleic_letters_3to1_extended)
    mapper["DN"] = "N"
    mapper["N"] = "N"
    new_mapper = strip_key_val(mapper)
    return new_mapper


def __protein_3to1_mapper():
    mapper = deepcopy(protein_letters_3to1_extended)
    mapper["UNK"] = "X"
    new_mapper = strip_key_val(mapper)
    return new_mapper


nucleic_3to1_mapper = __nucleic_3to1_mapper()
protein_3to1_mapper = __protein_3to1_mapper()
