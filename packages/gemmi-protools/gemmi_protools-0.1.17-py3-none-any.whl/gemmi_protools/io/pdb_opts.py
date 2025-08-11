"""
@Author: Luo Jiejian
"""
import gzip
import io
import pathlib
import re
from collections import defaultdict
from typing import Dict, Union, List

from typeguard import typechecked

from gemmi_protools.io.parse_pdb_header import _parse_pdb_header_list
from gemmi_protools.io.struct_info import Entity


@typechecked
def _molecule_information(header_dict: Dict) -> Entity:
    entity2description = dict()
    entity2species = dict()
    entity2taxid = dict()

    for idx in header_dict["compound"].keys():
        compound = header_dict["compound"][idx]
        if "chain" in compound:
            chain = re.sub(pattern=r"\s+", repl="", string=compound["chain"])
            if chain != "":
                tmp = chain.split(",")
                tmp.sort()
                key = ",".join(tmp)

                molecule = compound.get("molecule", "")

                if idx in header_dict["source"]:
                    source = header_dict["source"][idx]
                    specie = source.get("organism_scientific", "")
                    taxid = source.get("organism_taxid", "")
                else:
                    specie = ""
                    taxid = ""

                entity2description[key] = molecule
                entity2species[key] = specie
                entity2taxid[key] = taxid

    vals = dict(eid2desc=entity2description,
                eid2specie=entity2species,
                eid2taxid=entity2taxid,
                polymer2eid=dict()
                )
    return Entity(**vals)


@typechecked
def _is_pdb(path: Union[str, pathlib.Path]) -> bool:
    if isinstance(path, str):
        path = pathlib.Path(path)
    if path.suffixes:
        if path.suffixes[-1] == ".pdb":
            return True
        elif "".join(path.suffixes[-2:]) == ".pdb.gz":
            return True
        else:
            return False
    else:
        return False


# add by Ljj
@typechecked
def _pdb_entity_info(path: Union[str, pathlib.Path]) -> Entity:
    if _is_pdb(path):
        cur_path = pathlib.Path(path)
        if cur_path.suffixes[-1] == ".pdb":
            with open(path, "r") as text_io:
                lines = text_io.readlines()
        else:
            with gzip.open(path, "rb") as gz_handle:
                with io.TextIOWrapper(gz_handle, encoding="utf-8") as text_io:
                    lines = text_io.readlines()
    else:
        raise ValueError("Only support .pdb or .pdb.gz file, but got %s" % path)

    i = 0
    for i in range(len(lines)):
        line = lines[i]
        record_type = line[0:6]
        if record_type in ("ATOM  ", "HETATM", "MODEL "):
            break

    header = lines[0:i]
    info = _parse_pdb_header_list(header)
    return _molecule_information(info)


@typechecked
def _get_pdb_resolution(remark_lines: List[str]) -> float:
    resolutions = []
    for line in remark_lines:
        tmp = re.search(r"REMARK.+RESOLUTION.+?([\d\.]+|NOT APPLICABLE)", line)
        if tmp:
            v = tmp.groups()[0]
            try:
                vf = float(v)
            except (TypeError, ValueError):
                continue
            else:
                resolutions.append(vf)
    if resolutions:
        return min(resolutions)
    else:
        return 0.0


@typechecked
def _compound_source_string(entity: Entity) -> List[str]:
    entity2polymer = defaultdict(list)
    for k, v in entity["polymer2eid"].items():
        entity2polymer[v].append(k)
    entity_labels = list(entity2polymer.keys())
    entity_labels.sort()
    for v in entity2polymer.values():
        v.sort()

    values = []
    for i, el in enumerate(entity_labels):
        values.append(dict(mol_id=str(i + 1),
                           chain=", ".join(entity2polymer[el]),
                           molecule=entity["eid2desc"].get(el, "?"),
                           organism_scientific=entity["eid2specie"].get(el, "?"),
                           organism_taxid=entity["eid2taxid"].get(el, "?")
                           )
                      )
    outputs = []
    # compound
    compound_mol0 = "COMPND    MOL_ID: {mol_id};"
    compound_mol1 = "COMPND {n_line:>3} MOL_ID: {mol_id};"
    compound_molecule = "COMPND {n_line:>3} MOLECULE: {molecule};"
    compound_chain = "COMPND {n_line:>3} CHAIN: {chain};"

    i = 1
    for val in values:
        if i == 1:
            outputs.append(compound_mol0.format(**val))
            i += 1
            for c_str in [compound_molecule, compound_chain]:
                cur_val = val.copy()
                cur_val["n_line"] = i
                outputs.append(c_str.format(**cur_val))
                i += 1
        else:
            for c_str in [compound_mol1, compound_molecule, compound_chain]:
                cur_val = val.copy()
                cur_val["n_line"] = i
                outputs.append(c_str.format(**cur_val))
                i += 1

    source_mol0 = "SOURCE    MOL_ID: {mol_id};"
    source_mol1 = "SOURCE {n_line:>3} MOL_ID: {mol_id};"
    source_scientific = "SOURCE {n_line:>3} ORGANISM_SCIENTIFIC: {organism_scientific};"
    source_taxid = "SOURCE {n_line:>3} ORGANISM_TAXID: {organism_taxid};"

    i = 0
    for val in values:
        if i == 0:
            outputs.append(source_mol0.format(**val))
            i += 1
            for c_str in [source_scientific, source_taxid]:
                cur_val = val.copy()
                cur_val["n_line"] = i
                outputs.append(c_str.format(**cur_val))
                i += 1
        else:
            for c_str in [source_mol1, source_scientific, source_taxid]:
                cur_val = val.copy()
                cur_val["n_line"] = i
                outputs.append(c_str.format(**cur_val))
                i += 1
    return outputs
