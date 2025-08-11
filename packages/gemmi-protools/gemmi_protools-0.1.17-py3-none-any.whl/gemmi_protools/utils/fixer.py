"""
@Author: Luo Jiejian
@Date: 2025/1/21
"""
import gzip
import io
import os
import pathlib
import re
import shutil
import subprocess
import time
import uuid
from typing import Union

import openmm
import pdbfixer
from openmm import app
from typeguard import typechecked

from gemmi_protools import StructureParser
from gemmi_protools.io.cif_opts import _is_cif
from gemmi_protools.io.pdb_opts import _is_pdb


@typechecked
def _load_by_pbdfixer(path: Union[str, pathlib.Path], cpu_platform=True) -> pdbfixer.PDBFixer:
    """

    Args:
        path:
        cpu_platform: default True, if False, auto select platform

    Returns:

    """
    if cpu_platform:
        platform = openmm.Platform.getPlatformByName('CPU')
    else:
        platform = None

    cur_path = pathlib.Path(path)
    if _is_pdb(path) or _is_cif(path):
        s1 = cur_path.suffixes[-1]
        s2 = "".join(cur_path.suffixes[-2:])

        if s1 in [".pdb", ".cif"]:
            # s1 suffix
            fixer = pdbfixer.PDBFixer(filename=path, platform=platform)
        else:
            # s2 suffix
            with gzip.open(path, "rb") as gz_handle:
                with io.TextIOWrapper(gz_handle, encoding="utf-8") as text_io:
                    if s2 == ".pdb.gz":
                        fixer = pdbfixer.PDBFixer(pdbfile=text_io, platform=platform)
                    else:
                        fixer = pdbfixer.PDBFixer(pdbxfile=text_io, platform=platform)
    else:
        raise ValueError("Only support .cif, .cif.gz, .pdb or .pdb.gz file, but got %s" % path)
    return fixer


@typechecked
def clean_structure(input_file: Union[str, pathlib.Path],
                    output_file: Union[str, pathlib.Path],
                    add_missing_residue: bool = False,
                    add_missing_atoms: str = "heavy",
                    keep_heterogens: str = "all",
                    replace_nonstandard: bool = True,
                    ph: Union[float, int] = 7.0,
                    cpu_platform=True,
                    clean_connect=True
                    ):
    """

    :param input_file: str, Input structure file, support file format .cif, .cif.gz, .pdb or .pdb.gz
    :param output_file: str, Output structure file, support file format .cif, .pdb
    :param add_missing_residue: default False
    :param add_missing_atoms: default heavy, accepted values 'all', 'heavy', 'hydrogen', 'none'
        all: add missing heavy and hydrogen atoms
        heavy: add missing heavy atoms only
        hydrogen: add missing hydrogen atoms only
        none: not add missing atoms

    :param keep_heterogens: default all, accepted values 'all', 'water', 'none'
            all: keep all heterogens
            water: only keep water
            none: remove all heterogens
    :param replace_nonstandard: default True, replace all non-standard residues to standard ones
    :param ph: default 7.0, ph values to add missing hydrogen atoms
    :param cpu_platform: default True to use CPU platform, if False, auto select platform
    :param clean_connect: default True to clean CONECT lines in output pdb

    :return:
        str, status message of fixing
        if successful, return Finish, otherwise message of error
    """
    assert add_missing_atoms in ['all', 'heavy', 'hydrogen', 'none']
    assert keep_heterogens in ['all', 'water', 'none']

    try:
        ######################################################
        # load structure
        ######################################################
        fixer = _load_by_pbdfixer(input_file, cpu_platform)

        ######################################################
        # check
        ######################################################
        fixer.findMissingResidues()
        fixer.findMissingAtoms()
        ratio = "%.2f" % (len(fixer.missingAtoms) / fixer.topology.getNumResidues(),)

        ######################################################
        # replace non-standard residues
        ######################################################
        if replace_nonstandard:
            fixer.findNonstandardResidues()
            fixer.replaceNonstandardResidues()

        ######################################################
        # remove heterogens
        ######################################################
        if keep_heterogens == 'none':
            fixer.removeHeterogens(keepWater=False)
        elif keep_heterogens == 'water':
            fixer.removeHeterogens(keepWater=True)

        ######################################################
        # missing residue
        ######################################################
        if add_missing_residue:
            fixer.findMissingResidues()
        else:
            fixer.missingResidues = {}

        ######################################################
        # missing atoms
        ######################################################
        fixer.findMissingAtoms()
        if add_missing_atoms not in ['all', 'heavy']:
            fixer.missingAtoms = {}
            fixer.missingTerminals = {}
        fixer.addMissingAtoms()
        if add_missing_atoms in ['all', 'hydrogen']:
            fixer.addMissingHydrogens(ph)

        ######################################################
        # output
        ######################################################
        out_dir = os.path.dirname(output_file)
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        suffix = pathlib.Path(output_file).suffix
        assert suffix in [".pdb", ".cif"], "output file must be .cif or .pdb"

        with open(output_file, 'w') as out_handle:
            if suffix == ".pdb":
                app.PDBFile.writeFile(fixer.topology, fixer.positions, out_handle, keepIds=True)
            else:
                app.PDBxFile.writeFile(fixer.topology, fixer.positions, out_handle, keepIds=True)

        msg_str = "Finished"
    except Exception as e:
        msg_str = str(e)
        ratio = "*"
    else:
        if clean_connect:
            output_lines = []
            with open(output_file, "r") as in_handle:
                for line in in_handle:
                    if not re.match("CONECT", line):
                        output_lines.append(line)
            with open(output_file, "w") as out_handle:
                print("".join(output_lines), file=out_handle)

    return dict(input=input_file, msg=msg_str, res_ratio_with_missing_atoms=ratio)


@typechecked
def repair_structure(input_file: str,
                     output_file: str,
                     complex_with_dna: bool = False,
                     complex_with_rna: bool = False,
                     timeout: Union[int, float] = 3600):
    """

    :param input_file: .pdb or .cif or .pdb.gz or .cif.gz
    :param output_file: .pdb file
    :param complex_with_dna: bool, default False, not debug yet
    :param complex_with_rna: bool, default False, not debug yet
    :param timeout: float or int
    :return:
    """
    ############################################################
    # Check and convert input_file to .pdb if not
    ############################################################
    input_file = str(pathlib.Path(input_file).expanduser().resolve())
    output_file = str(pathlib.Path(output_file).expanduser().resolve())
    # input_file and output_file can't be the same path
    assert input_file != output_file, "input_file and output_file can't be the same path"

    assert os.path.splitext(output_file)[1] == ".pdb", "output_file Not .pdb: %s" % output_file
    assert _is_cif(input_file) or _is_pdb(input_file), "Not .pdb or .cif or .pdb.gz or .cif.gz: %s" % input_file

    ############################################################
    # Config Path
    ############################################################
    out_dir = os.path.dirname(output_file)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    temp_dir = os.path.join(out_dir, "_RepairTemp_%s" % str(uuid.uuid4()))
    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # for fix the filename bug of foldx
    # rename the input always and save to .pdb
    # convert to .pdb
    st = StructureParser()
    st.load_from_file(input_file)
    # if exist non-1-letter chain ID, rename
    org2new = st.make_chain_names_to_one_letter()

    file_name_r = "in.pdb"
    in_dir_r = temp_dir
    st.to_pdb(os.path.join(in_dir_r, file_name_r))

    foldx_path = shutil.which("foldx")
    if foldx_path is None:
        raise RuntimeError("path of foldx is not set or found in PATH")

    cwd_dir = os.getcwd()

    repair_cmd = [foldx_path,
                  "-c RepairPDB",
                  "--pdb %s" % file_name_r,
                  "--pdb-dir %s" % in_dir_r,
                  "--output-dir %s" % temp_dir
                  ]
    if complex_with_dna:
        repair_cmd.append("--complexWithDNA true")

    if complex_with_rna:
        repair_cmd.append("--complexWithRNA true")

    command_settings = ["cd %s &&" % temp_dir] + repair_cmd + ["&& cd %s" % cwd_dir]
    start = time.time()
    try:
        result = subprocess.run(" ".join(command_settings), shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=timeout)
        # Return a tuple of the file name and the stdout or stderr if command fails
        if result.returncode == 0:
            msg_str = "Finished"
        else:
            msg_str = str(result.stderr)
    except Exception as e:
        msg_str = str(e)
    else:
        if msg_str == "Finished":
            # just keep .pdb, ignore .fxout
            result_file = os.path.join(temp_dir, "in_Repair.pdb")
            if os.path.exists(result_file):
                shutil.move(result_file, output_file)
            else:
                msg_str = "result file not found"
    finally:
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
    end = time.time()
    return dict(input=input_file, output=output_file, msg=msg_str, use_time=round(end - start, 1))
