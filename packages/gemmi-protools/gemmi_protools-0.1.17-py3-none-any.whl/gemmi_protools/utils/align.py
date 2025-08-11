"""
@Author: Luo Jiejian
"""
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import uuid
from copy import deepcopy
from typing import Union, Dict, Any, List, Optional

import numpy as np
from Bio.PDB import Superimposer
from typeguard import typechecked

from gemmi_protools.io.convert import gemmi2bio, bio2gemmi
from gemmi_protools.io.reader import StructureParser


class StructureAligner(object):
    @typechecked
    def __init__(self, query_path: Union[str, pathlib.Path], ref_path: Union[str, pathlib.Path]):
        self._query_st = StructureParser()
        self._query_st.load_from_file(query_path)
        self._query_st.set_default_model()

        self._ref_st = StructureParser()
        self._ref_st.load_from_file(ref_path)
        self._ref_st.set_default_model()

        self.values = dict()
        self.rot_mat = None
        self.is_aligned = False
        self.by_query = None
        self.by_ref = None
        self.query_path = query_path
        self.ref_path = ref_path

    @property
    def __mmalign_path(self):
        _path = shutil.which("MMAlign") or shutil.which("MMalign")
        if _path is None:
            raise RuntimeError("Executable program MMAlign is not found. "
                               "Download from https://zhanggroup.org/MM-align/ ."
                               "Build it and add MMAlign to environment PATH")
        else:
            return _path

    @staticmethod
    @typechecked
    def __parser_rotation_matrix(matrix_file: Union[str, pathlib.Path]):
        rotation_matrix = []
        translation_vector = []

        with open(matrix_file, 'r') as file:
            lines = file.readlines()
            values = lines[2:5]
            for cur_line in values:
                tmp = re.split(pattern=r"\s+", string=cur_line.strip())
                assert len(tmp) == 5
                rotation_matrix.append(tmp[2:])
                translation_vector.append(tmp[1])
        return dict(R=np.array(rotation_matrix).astype(np.float32),
                    T=np.array(translation_vector).astype(np.float32))

    @staticmethod
    @typechecked
    def __parse_terminal_outputs(output_string: str) -> Dict[str, Any]:
        lines = re.split(pattern=r"\n", string=output_string)
        # chain mapping
        patterns = dict(query_chain_ids=r"Structure_1.+\.pdb:([\w:]+)",
                        ref_chain_ids=r"Structure_2.+\.pdb:([\w:]+)",
                        query_total_length=r"Length of Structure_1.*?(\d+).*residues",
                        ref_total_length=r"Length of Structure_2.*?(\d+).*residues",
                        aligned_length=r"Aligned length=.*?(\d+)",
                        rmsd=r"RMSD=.*?([\d.]+)",
                        tmscore_by_query=r"TM-score=.*?([\d.]+).+Structure_1",
                        tmscore_by_ref=r"TM-score=.*?([\d.]+).+Structure_2",
                        aligned_seq_start=r"denotes other aligned residues",
                        )

        values = dict()
        for idx, line in enumerate(lines):
            current_keys = list(patterns.keys())
            for key in current_keys:
                tmp = re.search(patterns[key], line)
                if tmp:
                    if key in ['query_chain_ids', 'ref_chain_ids']:
                        values[key] = re.split(pattern=":", string=tmp.groups()[0])
                        del patterns[key]
                    elif key in ['query_total_length', 'ref_total_length', 'aligned_length']:
                        values[key] = int(tmp.groups()[0])
                        del patterns[key]
                    elif key in ['rmsd', 'tmscore_by_query', 'tmscore_by_ref']:
                        values[key] = float(tmp.groups()[0])
                        del patterns[key]
                    elif key == "aligned_seq_start":
                        # idx + 1 and idx + 3 for aligned sequences 1 and 2
                        seq_1 = lines[idx + 1]
                        seq_2 = lines[idx + 3]

                        sp1 = re.split(pattern=r"\*", string=seq_1)
                        sp2 = re.split(pattern=r"\*", string=seq_2)
                        values["query_sequences"] = sp1[:-1] if "*" in seq_1 else sp1
                        values["ref_sequences"] = sp2[:-1] if "*" in seq_2 else sp2
                        del patterns[key]
        return values

    @typechecked
    def make_alignment(self, query_chains: Optional[List[str]] = None,
                       ref_chains: Optional[List[str]] = None, timeout=300.0):
        """

        :param query_chains: list, None for all chains
        :param ref_chains: list, None for all chains
        :param timeout: default 300
        :return:
        """

        program_path = self.__mmalign_path

        # clone
        q_st = deepcopy(self._query_st)
        r_st = deepcopy(self._ref_st)

        tmp_dir = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        os.makedirs(tmp_dir)

        if isinstance(query_chains, list):
            q_st.pick_chains(query_chains)

        if isinstance(ref_chains, list):
            r_st.pick_chains(ref_chains)

        q_ch_mapper = q_st.make_chain_names_to_one_letter()
        r_ch_mapper = r_st.make_chain_names_to_one_letter()

        q_ch_mapper_r = {v: k for k, v in q_ch_mapper.items()}
        r_ch_mapper_r = {v: k for k, v in r_ch_mapper.items()}

        _tmp_a = os.path.join(tmp_dir, "a.pdb")
        q_st.to_pdb(_tmp_a)

        _tmp_b = os.path.join(tmp_dir, "b.pdb")
        r_st.to_pdb(_tmp_b)

        matrix_file = os.path.join(tmp_dir, "m.txt")
        _command = "%s %s %s -m %s" % (program_path, _tmp_a, _tmp_b, matrix_file)

        try:
            result = subprocess.run(_command, shell=True, check=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    timeout=timeout)
        except Exception as e:
            print("%s: between files %s and %s; between chains: %s and %s" % (
                str(e), self.query_path, self.ref_path,
                str(q_st.chain_ids), str(r_st.chain_ids))
                  )
        else:
            self.values = self.__parse_terminal_outputs(result.stdout.decode())
            self.rot_mat = self.__parser_rotation_matrix(matrix_file)
            self.is_aligned = True
            self.by_query = q_st.chain_ids if query_chains is None else query_chains
            self.by_ref = r_st.chain_ids if ref_chains is None else ref_chains
            self.values["query_chain_ids"] = [q_ch_mapper_r.get(ch, ch) for ch in self.values["query_chain_ids"]]
            self.values["ref_chain_ids"] = [r_ch_mapper_r.get(ch, ch) for ch in self.values["ref_chain_ids"]]

        finally:
            if os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir)

    @typechecked
    def save_aligned_query(self, out_file: str):
        """

        :param out_file: .cif file
        :return:
        """
        if not self.is_aligned:
            raise RuntimeError("structure not aligned, run make_alignment first")

        super_imposer = Superimposer()
        super_imposer.rotran = (self.rot_mat["R"].T, self.rot_mat["T"])

        bio_s = gemmi2bio(self._query_st.STRUCT)
        super_imposer.apply(bio_s)
        query_st_aligned = bio2gemmi(bio_s)

        block = query_st_aligned.make_mmcif_block()
        block.write_file(out_file)
