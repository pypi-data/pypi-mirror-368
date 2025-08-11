"""
@Author: Luo Jiejian
"""

import pathlib
from typing import Union, Dict, Any

import gemmi
import pandas as pd
from typeguard import typechecked

from gemmi_protools.io.struct_info import Entity


@typechecked
def _is_cif(path: Union[str, pathlib.Path]) -> bool:
    if isinstance(path, str):
        path = pathlib.Path(path)
    if path.suffixes:
        if path.suffixes[-1] == ".cif":
            return True
        elif "".join(path.suffixes[-2:]) == ".cif.gz":
            return True
        else:
            return False
    else:
        return False


@typechecked
def _value_mapper_from_block(block: gemmi.cif.Block, category: str, column1: str, column2: str,
                             expand_column1: bool = False) -> Dict[str, Any]:
    """
    mapper from column1 to column2
    :param block:
    :param category:
    :param column1:
    :param column2:
    :param expand_column1: bool, if True, values joint by comma in column1 with be split
    :return:
    Only return a mapper when both column1 and column2 in category
    """
    loop = block.find_mmcif_category(category)
    tags = list(loop.tags)

    results = dict()
    if column1 in tags:
        values1 = loop.column(tags.index(column1))
        v1 = [values1.str(i) for i in range(len(values1))]

        if column2 in tags:
            values2 = loop.column(tags.index(column2))
            v2 = [values2.str(i) for i in range(len(values2))]
        else:
            v2 = ["?"] * len(v1)

        outputs = dict(zip(v1, v2))

        if expand_column1:
            outputs_ex = dict()
            for key, val in outputs.items():
                tmp = key.split(",")
                for sk in tmp:
                    nk = sk.strip()
                    if nk:
                        outputs_ex[nk] = val
            results = outputs_ex
        else:
            results = outputs
    return results


@typechecked
def _get_cif_resolution(block: gemmi.cif.Block) -> float:
    resolution = 0.0
    for key in ["_reflns.d_resolution_high",
                "_refine.ls_d_res_high",
                "_refine_hist.d_res_high",
                "_em_3d_reconstruction.resolution",
                ]:
        v = block.find_value(key)
        try:
            vf = float(v)
        except (TypeError, ValueError):
            continue
        else:
            resolution = vf
            break
    return resolution


@typechecked
def _cif_entity_info(block: gemmi.cif.Block) -> Entity:
    entity2description = _value_mapper_from_block(block, category="_entity.",
                                                  column1="_entity.id",
                                                  column2="_entity.pdbx_description")

    polymer2entity = _value_mapper_from_block(block, category="_entity_poly.",
                                              column1="_entity_poly.pdbx_strand_id",
                                              column2="_entity_poly.entity_id",
                                              expand_column1=True)
    entity2species = _value_mapper_from_block(block, category="_entity_src_gen.",
                                              column1="_entity_src_gen.entity_id",
                                              column2="_entity_src_gen.pdbx_gene_src_scientific_name")

    entity2species.update(_value_mapper_from_block(block, category="_pdbx_entity_src_syn.",
                                                   column1="_pdbx_entity_src_syn.entity_id",
                                                   column2="_pdbx_entity_src_syn.organism_scientific")
                          )
    entity2species.update(_value_mapper_from_block(block, category="_entity_src_nat.",
                                                   column1="_entity_src_nat.entity_id",
                                                   column2="_entity_src_nat.pdbx_organism_scientific")
                          )
    entity2taxid = _value_mapper_from_block(block, category="_entity_src_gen.",
                                            column1="_entity_src_gen.entity_id",
                                            column2="_entity_src_gen.pdbx_gene_src_ncbi_taxonomy_id")
    entity2taxid.update(_value_mapper_from_block(block, category="_pdbx_entity_src_syn.",
                                                 column1="_pdbx_entity_src_syn.entity_id",
                                                 column2="_pdbx_entity_src_syn.ncbi_taxonomy_id")
                        )
    entity2taxid.update(_value_mapper_from_block(block, category="_entity_src_nat.",
                                                 column1="_entity_src_nat.entity_id",
                                                 column2="_entity_src_nat.pdbx_ncbi_taxonomy_id")
                        )

    vals = dict(eid2desc=entity2description,
                eid2specie=entity2species,
                eid2taxid=entity2taxid,
                polymer2eid=polymer2entity
                )
    return Entity(**vals)


@typechecked
def _cif_block_for_output(structure: gemmi.Structure, entity: Entity) -> gemmi.cif.Block:
    block = structure.make_mmcif_block()

    reflns = block.find_mmcif_category(category="_reflns.")
    resolution = "%.2f" % structure.resolution
    reflns.erase()
    reflns_loop = block.init_loop(prefix="_reflns.", tags=["d_resolution_high", "d_resolution_low"])
    reflns_loop.add_row([resolution, resolution])

    ta = block.find_mmcif_category(category="_entity.")
    da = pd.DataFrame(list(ta), columns=list(ta.tags))
    if "_entity.id" in da.columns:
        da["_entity.pdbx_description"] = da["_entity.id"].apply(
            lambda i: entity["eid2desc"].get(i, "?").strip() or "?")

        rows = []
        for ar in da.to_numpy().tolist():
            rows.append([gemmi.cif.quote(i) for i in ar])

        if "_entity.pdbx_description" not in list(ta.tags):
            ta.loop.add_columns(["_entity.pdbx_description"], "?")

        ta = block.find_mmcif_category(category="_entity.")
        for _ in range(len(ta)):
            ta.remove_row(0)
        for row in rows:
            ta.append_row(row)

    loop = block.init_loop("_entity_src_gen.", ["entity_id",
                                                "pdbx_gene_src_scientific_name",
                                                "pdbx_gene_src_ncbi_taxonomy_id"])

    for k in entity["eid2specie"].keys():
        loop.add_row([gemmi.cif.quote(k),
                      gemmi.cif.quote(entity["eid2specie"].get(k, "?")),
                      gemmi.cif.quote(entity["eid2taxid"].get(k, "?"))]
                     )
    block.move_item(-1, 16)
    return block
