"""
@Author: Luo Jiejian
"""
import pathlib
import string
import warnings
from copy import deepcopy
from typing import Union, Optional, List

import gemmi
import numpy as np
from typeguard import typechecked

from gemmi_protools.io.cif_opts import _cif_block_for_output, _is_cif
from gemmi_protools.io.parser import (_assign_digital_entity_names, _ent_from_structure,
                                      pdb_parser, cif_parser, _chain_type, _chain_names2one_letter,
                                      _assert_unique_chain_names_in_models, get_assembly)
from gemmi_protools.io.pdb_opts import _compound_source_string, _is_pdb
from gemmi_protools.io.peptide import nucleic_3to1_mapper, protein_3to1_mapper
from gemmi_protools.io.struct_info import Info


class StructureParser(object):
    """
    Enhance Structure reader for .cif, .cif.gz, .pdb or .pdb.gz
    """

    def __init__(self, structure: gemmi.Structure = None):
        if not isinstance(structure, (type(None), gemmi.Structure)):
            raise ValueError("structure must be gemmi.Structure or None")
        if structure is None:
            self.STRUCT = gemmi.Structure()
        elif isinstance(structure, gemmi.Structure):
            _assert_unique_chain_names_in_models(structure)
            self.STRUCT = structure.clone()
        else:
            raise ValueError("structure must be gemmi.Structure or None")
        self.STRUCT.setup_entities()
        _assign_digital_entity_names(self.STRUCT)

        self.INFO = Info()
        self.INFO.from_gemmi_structure_infomap(self.STRUCT.info)
        self.ENTITY = _ent_from_structure(self.STRUCT)
        self.update_entity()
        self.update_full_sequences()

    def update_full_sequences(self):
        for ent_idx, ent in enumerate(self.STRUCT.entities):
            # get full sequence
            full_seq = ent.full_sequence

            # when missing, construct from Residues
            if not full_seq:
                sel_ch_id = None
                sel_ch_len = 0
                for ch_id, ent_id in self.ENTITY.polymer2eid.items():
                    if ent_id == ent.name:
                        cur_len = len(self.polymer_sequences[ch_id])
                        if cur_len > sel_ch_len:
                            sel_ch_id = ch_id
                            sel_ch_len = cur_len

                if sel_ch_id is not None and sel_ch_len > 0:
                    full_seq = [r.name for r in self.STRUCT[0][sel_ch_id].get_polymer() if not r.is_water()]
                    self.STRUCT.entities[ent_idx].full_sequence = full_seq

    @typechecked
    def load_from_file(self, path: Union[str, pathlib.PosixPath]):
        if _is_pdb(path):
            struct, entity = pdb_parser(path)
        elif _is_cif(path):
            struct, entity = cif_parser(path)
        else:
            raise ValueError("Only support .cif, .cif.gz, .pdb or .pdb.gz file, but got %s" % path)

        _assert_unique_chain_names_in_models(struct)
        self.STRUCT, self.ENTITY = struct, entity
        self.INFO.from_gemmi_structure_infomap(self.STRUCT.info)
        self.update_entity()
        self.update_full_sequences()

    @typechecked
    def to_pdb(self, outfile: str, write_minimal_pdb=False):
        compound_source = _compound_source_string(self.ENTITY)
        struct = self.STRUCT.clone()

        rs = "REMARK   2 RESOLUTION.    %.2f ANGSTROMS." % struct.resolution
        resolution_remarks = ["%-80s" % "REMARK   2",
                              "%-80s" % rs]

        struct.raw_remarks = compound_source + resolution_remarks
        if write_minimal_pdb:
            struct.write_minimal_pdb(outfile)
        else:
            struct.write_pdb(outfile)

    @typechecked
    def to_cif(self, outfile: str):
        out_block = _cif_block_for_output(self.STRUCT, self.ENTITY)
        out_block.write_file(outfile)

    @property
    def chain_ids(self):
        vals = []
        for m in self.STRUCT:
            for c in m:
                vals.append(c.name)
        vals.sort()
        return vals

    @property
    def model_numbers(self):
        return [m.num for m in self.STRUCT]

    @typechecked
    def set_default_model(self, num: Optional[int] = None):
        """
        Set the first model as default
        :param num:
        :return:
        """
        if len(self.STRUCT) == 0:
            raise RuntimeError("There is no model in structure")

        keep_model = None
        if num is None:
            # default first model
            keep_model = self.STRUCT[0]
        else:
            for model in self.STRUCT:
                if model.num == num:
                    keep_model = model
                    break

        if keep_model is None:
            raise RuntimeError("Model %d not found in structure" % num)

        # del, reversed order indexes
        indexes_to_del = [i for i, model in enumerate(self.STRUCT) if model.num != keep_model.num]
        indexes_to_del.sort(reverse=True)

        for cur_index in indexes_to_del:
            del self.STRUCT[cur_index]

    @property
    def chain_types(self):
        return {c: _chain_type(self.STRUCT, c) for c in self.chain_ids}

    @property
    def assembly_names(self):
        return [assem.name for assem in self.STRUCT.assemblies]

    @property
    def polymer_sequences(self):
        cts = self.chain_types
        out = dict()
        for model in self.STRUCT:
            for chain in model:
                ct = cts.get(chain.name, "other")
                if ct != "other":
                    out[chain.name] = self.make_one_letter_sequence(chain.name)
        return out

    @property
    def polymer_residue_numbers(self):
        cts = self.chain_types
        out = dict()
        id_type = np.dtype([
            ("ch_name", "U5"),
            ("res_num", "i4"),
            ("res_icode", "U3"),
            ("res_name", "U5"),
        ])
        for model in self.STRUCT:
            for chain in model:
                ct = cts.get(chain.name, "other")
                if ct != "other":
                    out[chain.name] = np.array([(chain.name, r.seqid.num, r.seqid.icode, r.name)
                                                for r in chain.get_polymer()], dtype=id_type)
        return out

    def chain_residues(self, polymer_only=True, with_water=False):
        """
        :param polymer_only, bool
        :param with_water:
        :return: dict of Three-letter codes of chain residues
        """

        out = dict()
        for model in self.STRUCT:
            for chain in model:
                res_codes = []
                for r in chain:
                    if r.is_water():
                        if with_water:
                            res_codes.append(r.name)
                    else:
                        if polymer_only:
                            if r.entity_type.name == "Polymer":
                                res_codes.append(r.name)
                        else:
                            res_codes.append(r.name)
                out[chain.name] = res_codes
        return out

    def update_entity(self):
        """
        Update ENTITY, .entities .assemblies according to subchains
        :return:
        """
        subchains = []
        for model in self.STRUCT:
            for chain in model:
                subchains.extend([sc.subchain_id() for sc in chain.subchains()])

        # update .entities
        new_entities = gemmi.EntityList()
        ent_names = []  # keep
        for ent in self.STRUCT.entities:
            tmp = [i for i in ent.subchains if i in subchains]
            if tmp:
                ent.subchains = tmp
                new_entities.append(ent)
                ent_names.append(ent.name)
        self.STRUCT.entities = new_entities

        # update .ENTITY
        for super_key in ["eid2desc", "eid2specie", "eid2taxid"]:
            for eid in list(self.ENTITY[super_key].keys()):
                if eid not in ent_names:
                    del self.ENTITY[super_key][eid]

        for cid, eid in list(self.ENTITY["polymer2eid"].items()):
            if eid not in ent_names or cid not in self.chain_ids:
                del self.ENTITY["polymer2eid"][cid]

        # update .assemblies
        all_cid = self.chain_ids
        del_assembly_indexes = []

        for a_i, assembly in enumerate(self.STRUCT.assemblies):
            del_gen_indexes = []
            for g_i, gen in enumerate(assembly.generators):
                # chains
                tmp1 = [i for i in gen.chains if i in all_cid]
                gen.chains = tmp1

                tmp2 = [i for i in gen.subchains if i in subchains]
                gen.subchains = tmp2
                # empty gen
                if gen.chains == [] and gen.subchains == []:
                    del_gen_indexes.append(g_i)

            del_gen_indexes.sort(reverse=True)
            for dgi in del_gen_indexes:
                del assembly.generators[dgi]

            if len(del_gen_indexes) == len(assembly.generators):
                del_assembly_indexes.append(a_i)

        del_assembly_indexes.sort(reverse=True)
        for dai in del_assembly_indexes:
            del self.STRUCT.assemblies[dai]

    @typechecked
    def rename_chain(self, origin_name: str, target_name: str):
        if origin_name not in self.chain_ids:
            raise ValueError("chain %s not found" % origin_name)
        other_chain_names = set(self.chain_ids) - {origin_name}

        if target_name in other_chain_names:
            raise ValueError("target chain name %s has existed, change to a different one." % target_name)

        self.STRUCT.rename_chain(origin_name, target_name)

        # update .polymer2eid if exist
        if origin_name in self.ENTITY.polymer2eid:
            val = self.ENTITY.polymer2eid[origin_name]
            del self.ENTITY.polymer2eid[origin_name]
            self.ENTITY.polymer2eid[target_name] = val

        # update .assemblies.generator.chain if exists, for .pdb loading structure
        for assembly in self.STRUCT.assemblies:
            for gen in assembly.generators:
                tmp = [target_name if c == origin_name else c for c in gen.chains]
                gen.chains = tmp

    @typechecked
    def switch_chain_names(self, chain_name_1: str, chain_name_2: str):
        if chain_name_1 not in self.chain_ids:
            raise ValueError("chain_name_2 %s not in structure" % chain_name_1)
        if chain_name_2 not in self.chain_ids:
            raise ValueError("chain_name_2 %s not in structure" % chain_name_2)

        l3 = [i + j + k for i in string.ascii_uppercase for j in string.ascii_uppercase for k in string.ascii_uppercase]
        l3.sort(reverse=True)

        current_names = set(self.chain_ids)
        l3_l = [n for n in l3 if n not in current_names]
        sw_name = l3_l.pop()
        self.rename_chain(chain_name_1, sw_name)
        self.rename_chain(chain_name_2, chain_name_1)
        self.rename_chain(sw_name, chain_name_2)

    @typechecked
    def pick_chains(self, chain_names: List[str]):
        self.set_default_model()

        if chain_names:
            missing = [c for c in chain_names if c not in self.chain_ids]
            if missing:
                raise ValueError("Chains %s not found" % ",".join(missing))
            else:
                del_chain_names = set(self.chain_ids) - set(chain_names)
                del_chain_indexes = [i for i, ch in enumerate(self.STRUCT[0]) if ch.name in del_chain_names]
                del_chain_indexes.sort(reverse=True)
                for di in del_chain_indexes:
                    del self.STRUCT[0][di]
                self.update_entity()
        else:
            raise ValueError("No chain is given")

    @typechecked
    def make_chain_names_to_one_letter(self, only_uppercase: bool = True):
        _mapper = _chain_names2one_letter(self.STRUCT, only_uppercase)
        for origin_name, target_name in _mapper.items():
            self.rename_chain(origin_name, target_name)
        return _mapper

    @typechecked
    def get_assembly(self, assembly_name: str):
        if assembly_name not in self.assembly_names:
            raise ValueError("assembly %s is not found" % assembly_name)

        struct, polymer2eid = get_assembly(self.STRUCT, assembly_name, gemmi.HowToNameCopiedChain.Short)
        out = StructureParser(struct)
        out.ENTITY = deepcopy(self.ENTITY)
        out.ENTITY.polymer2eid = polymer2eid

        # update info
        prefix = "[Assembly %s] " % assembly_name
        out.INFO.title = prefix + out.INFO.title
        out.STRUCT.info = out.INFO.to_gemmi_structure_infomap()
        return out

    @typechecked
    def merge_chains(self, chains: List[str]):
        """
        Merge a list of chains, target chain id is chains[0]

        Renumber the new chain from 1

        [No fix the Entity and some other information of structure]
        :param chains:
        :return:
        GemmiLoader
        """
        for c in chains:
            if c not in self.chain_ids:
                raise RuntimeError("Chain %s is not in the structure" % c)
        if len(self.STRUCT) > 1:
            print("Multiple models in structure, do nothing")
        elif len(chains) < 2:
            print("Query chains less than 2, do nothing")
        else:
            new_chain = gemmi.Chain(chains[0])
            residue_index = 1

            model = self.STRUCT[0]

            for ch in model:
                if ch.name in chains:
                    for res in ch:
                        nr = deepcopy(res)
                        nr.seqid.icode = " "
                        nr.seqid.num = residue_index
                        new_chain.add_residue(nr)
                        residue_index += 1

            for c in chains:
                self.STRUCT[0].remove_chain(c)

            self.STRUCT[0].add_chain(new_chain, unique_name=True)

    def get_atom_coords(self, chains: List[str], atoms: Optional[List[str]] = None):
        for c in chains:
            if c not in self.chain_ids:
                warnings.warn("Chain %s is not in the structure" % c)

        coord = []
        atom_id = []
        id_type = np.dtype([
            ("ch_name", "U5"),
            ("res_num", "i4"),
            ("res_icode", "U3"),
            ("res_name", "U5"),
            ("atom_name", "U5")
        ])

        model = self.STRUCT[0]
        for ch in model:
            if ch.name in chains:
                for res in ch:
                    for atom in res:
                        if atoms is None or atom.name in atoms:
                            cur_id = (ch.name, res.seqid.num, res.seqid.icode, res.name, atom.name)
                            cur_pos = atom.pos.tolist()
                            coord.append(cur_pos)
                            atom_id.append(cur_id)

        if coord:
            return np.array(coord, dtype=np.float32), np.array(atom_id, dtype=id_type)
        else:
            return np.empty(shape=(0, 3), dtype=np.float32), np.array(atom_id, dtype=id_type)

    def make_one_letter_sequence(self, chain_id):
        c_type = self.chain_types[chain_id]
        residues = self.chain_residues(polymer_only=True, with_water=False)[chain_id]

        if c_type == "protein":
            one_letter_code = "".join([protein_3to1_mapper.get(r, "X") for r in residues])
        elif c_type in ["dna", "rna"]:
            one_letter_code = "".join([nucleic_3to1_mapper.get(r, "N") for r in residues])
        else:
            one_letter_code = ""
        return one_letter_code

    def clean_structure(self, keep_ligand=True):
        """
        (1) remove_alternative_conformations
        (2) remove_hydrogens
        (3) remove_water
        (4) remove_empty_chains

        :return:
        """
        self.set_default_model()
        self.STRUCT.remove_alternative_conformations()
        self.STRUCT.remove_hydrogens()

        if keep_ligand:
            self.STRUCT.remove_waters()
        else:
            self.STRUCT.remove_ligands_and_waters()

        self.STRUCT.remove_empty_chains()

        # update information
        self.update_entity()
        self.update_full_sequences()
