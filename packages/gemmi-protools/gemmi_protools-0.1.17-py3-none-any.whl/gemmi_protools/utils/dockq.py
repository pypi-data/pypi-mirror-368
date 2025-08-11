"""
@Author: Luo Jiejian
"""
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import uuid
from typing import Optional, Union

import pandas as pd
from typeguard import typechecked

from gemmi_protools.io.reader import StructureParser


@typechecked
def _read_model(model_file: Union[str, pathlib.Path]):
    st = StructureParser()
    st.load_from_file(model_file)
    st.set_default_model()
    return st


@typechecked
def dockq_score(query_model: Union[str, pathlib.Path],
                native_model: Union[str, pathlib.Path],
                mapping: Optional[str] = None):
    dockq_program = shutil.which("DockQ")
    if dockq_program is None:
        raise RuntimeError("DockQ is need")

    q_st = _read_model(query_model)
    n_st = _read_model(native_model)

    tmp_dir = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    os.makedirs(tmp_dir)

    result_file = os.path.join(tmp_dir, "result.json")
    q_file = os.path.join(tmp_dir, "q.pdb")
    n_file = os.path.join(tmp_dir, "n.pdb")
    q_st.to_pdb(q_file, write_minimal_pdb=True)
    n_st.to_pdb(n_file, write_minimal_pdb=True)
    if mapping is None:
        cid = "".join(n_st.chain_ids)
        mapping = cid + ":" + cid

    _command = "%s --mapping %s --json %s %s %s" % (dockq_program, mapping, result_file, q_file, n_file)
    metrics = ['DockQ', 'F1', 'chain1', 'chain2']

    try:
        _ = subprocess.run(_command, shell=True, check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=300.0)
    except subprocess.CalledProcessError as e:
        # Handle errors in the called executable
        msg = e.stderr.decode()
        outputs = pd.DataFrame(columns=metrics)
    except Exception as e:
        # Handle other exceptions such as file not found or permissions issues
        msg = str(e)
        outputs = pd.DataFrame(columns=metrics)
    else:
        with open(result_file, "r") as fin:
            vals = json.load(fin)
        msg = "Finished"
        result = []
        for v in vals["best_result"].values():
            result.append(v)
        outputs = pd.DataFrame(result)[metrics]
    finally:
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)

    return dict(value=outputs,
                msg=msg,
                mapping=mapping,
                model=query_model,
                native=native_model
                )


def dockq_score_interface(query_model: Union[str, pathlib.Path],
                          native_model: Union[str, pathlib.Path],
                          chains_a: str,
                          chains_b: str):
    ppi_if = chains_a + "@" + chains_b
    chs_a = list(chains_a)
    chs_b = list(chains_b)

    # if multiple chains, merge to one
    q_st = _read_model(query_model)
    n_st = _read_model(native_model)

    for c in chs_a + chs_b:
        if c not in q_st.chain_ids:
            raise RuntimeError("Chain %s is not in the query model: %s" % (c, query_model))

    for c in chs_a + chs_b:
        if c not in n_st.chain_ids:
            raise RuntimeError("Chain %s is not in the native model: %s" % (c, native_model))

    if len(chs_a) > 1:
        q_st.merge_chains(chs_a)
        n_st.merge_chains(chs_a)

    if len(chs_b) > 1:
        q_st.merge_chains(chs_b)
        n_st.merge_chains(chs_b)

    tmp_dir = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    os.makedirs(tmp_dir)

    q_file = os.path.join(tmp_dir, "qm.pdb")
    n_file = os.path.join(tmp_dir, "nm.pdb")
    q_st.to_pdb(q_file, write_minimal_pdb=True)
    n_st.to_pdb(n_file, write_minimal_pdb=True)

    chs = chs_a[0] + chs_b[0]
    result = dockq_score(q_file, n_file, mapping="%s:%s" % (chs, chs))

    if len(result["value"]) > 0:
        q_score = round(result["value"].iloc[0]["DockQ"], 4)
        f1 = round(result["value"].iloc[0]["F1"], 4)
    else:
        q_score = ""
        f1 = ""

    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)

    return dict(DockQ=q_score,
                F1=f1,
                interface=ppi_if,
                model=query_model,
                native=native_model
                )
