"""
@Author: Luo Jiejian
"""
import pathlib
from typing import Union, List

import numpy as np
from scipy.spatial import cKDTree

from gemmi_protools.io.reader import StructureParser


def _ppi_atoms(struct, chains):
    """
    Load atoms for N and O of backbone and N, O, P, S of side chains, only for PPI searching
    :param struct:
    :param chains:
    :return:
    """
    protein_atoms = ['N', 'ND1', 'ND2', 'NE', 'NE1', 'NE2', 'NH1', 'NH2', 'NZ',
                     'O', 'OD1', 'OD2', 'OE1', 'OE2', 'OG', 'OG1', 'OH',
                     'SD', 'SG']
    xna_atoms = ['N1', 'N2', 'N3', 'N4', 'N6', 'N7', 'N9',
                 'O2', "O2'", "O3'", 'O4', "O4'", "O5'", 'O6',
                 'OP1', 'OP2', 'OP3', 'P']
    pro_chs = []
    xna_chs = []
    for c in chains:
        t = struct.chain_types.get(c, "")
        if t == "protein":
            pro_chs.append(c)
        elif t in ["dna", "rna"]:
            xna_chs.append(c)

    pro_coord, pro_id = struct.get_atom_coords(pro_chs, protein_atoms)
    xna_coord, xna_id = struct.get_atom_coords(xna_chs, xna_atoms)
    return np.concatenate([pro_coord, xna_coord], axis=0), np.concatenate([pro_id, xna_id], axis=0)


def ppi_interface_residues(in_file: Union[str, pathlib.Path],
                           chains_x: List[str],
                           chains_y: List[str],
                           threshold: float = 4.0):
    """
    identify PPI among protein, DNA, RNA
    :param in_file:
    :param chains_x:
    :param chains_y:
    :param threshold:
    :return:
     PPI residues of chains_x, PPI residues of chains_y
    """

    st = StructureParser()
    st.load_from_file(in_file)
    st.set_default_model()
    st.STRUCT.remove_alternative_conformations()
    st.STRUCT.remove_ligands_and_waters()
    st.STRUCT.remove_hydrogens()
    st.STRUCT.remove_empty_chains()
    st.update_entity()

    x_coord, x_id = _ppi_atoms(st, chains_x)
    y_coord, y_id = _ppi_atoms(st, chains_y)

    kd_tree_x = cKDTree(x_coord)
    kd_tree_y = cKDTree(y_coord)

    pairs = kd_tree_x.sparse_distance_matrix(kd_tree_y, threshold, output_type='coo_matrix')

    x_res = np.unique(x_id[pairs.row][["ch_name", 'res_num', 'res_icode', 'res_name']])
    y_res = np.unique(y_id[pairs.col][["ch_name", 'res_num', 'res_icode', 'res_name']])

    return x_res, y_res
