"""
@Author: Luo Jiejian
"""
import pathlib
from collections import Counter
from typing import Union, Optional, Dict, List

import gemmi
from typeguard import typechecked

from gemmi_protools.io.cif_opts import _cif_entity_info, _is_cif, _get_cif_resolution
from gemmi_protools.io.pdb_opts import _pdb_entity_info, _is_pdb, _get_pdb_resolution
from gemmi_protools.io.struct_info import Entity


@typechecked
def _ent_from_structure(struct: gemmi.Structure) -> Entity:
    """
    Run .setup_entities() in advance
    :param struct:
    :return:
    """
    block = struct.make_mmcif_block()
    ent_info = _cif_entity_info(block)
    for ent in struct.entities:
        if ent.name not in ent_info["eid2desc"]:
            ent_info["eid2desc"][ent.name] = ent.name
    return ent_info


@typechecked
def cif_parser(path: Union[str, pathlib.Path]):
    """
    Parse .cif or .cif.gz
    :param path:
    :return: (gemmi.Structure, entity)
    """
    if _is_cif(path):
        doc = gemmi.cif.read(str(path))
        block0 = doc.sole_block()
        struct = gemmi.read_structure(str(path))
        struct.setup_entities()
        # sheet_id like 1' will get some strange errors
        # result in sheets with 0 strands
        # delete sheets with 0 strands
        # check here

        zero_sheet_ind = []
        for i, sheet in enumerate(struct.sheets):
            if len(sheet.strands) == 0:
                zero_sheet_ind.append(i)

        if zero_sheet_ind:
            zero_sheet_ind.sort(reverse=True)
            for i in zero_sheet_ind:
                del struct.sheets[i]

        # gemmi fail to parse right resolution, update here
        struct.resolution = _get_cif_resolution(block0)

        # ent information
        # from doc
        ent_0 = _cif_entity_info(block0)

        # init from struct
        ent_1 = _ent_from_structure(struct)

        # update ent_0 with ent_1
        for super_key in ["eid2desc", "polymer2eid"]:
            for key, val in ent_1[super_key].items():
                if key not in ent_0[super_key]:
                    ent_0[super_key][key] = val
        return struct, ent_0
    else:
        raise ValueError("Only support .cif or .cif.gz file, but got %s" % path)


@typechecked
def _assign_digital_entity_names(structure: gemmi.Structure) -> Optional[Dict[str, str]]:
    """
    Run .setup_entities() in advance
    :param structure:
    :return:
    """
    # rename entities' names to numbers if not
    not_digit_name = False
    for ent in structure.entities:
        if not ent.name.isdigit():
            not_digit_name = True
            break

    if not_digit_name:
        mapper = dict()
        for ix, ent in enumerate(structure.entities):
            new_name = str(ix + 1)
            mapper[ent.name] = new_name
            ent.name = new_name
        return mapper
    else:
        return None


@typechecked
def _update_entity_names(entity: Entity, mapper: Dict[str, str]):
    """
    Update entity names to new ones in eid2desc, eid2specie, eid2taxid in place.
    :param entity:
    :param mapper: {old_entity_name: new_entity_name}
    :return:
    """
    for super_key in ['eid2desc', 'eid2specie', 'eid2taxid']:
        tmp = dict()
        for key in entity[super_key]:
            tmp[mapper[key]] = entity[super_key][key]
        entity.__setattr__(super_key, tmp)

    new_polymer2eid = dict()
    for c, old_eid in entity.polymer2eid.items():
        new_polymer2eid[c] = mapper[old_eid]
    entity.__setattr__(name="polymer2eid", value=new_polymer2eid)


def _melt_dict(inputs: dict):
    outputs = dict()
    for keys, val in inputs.items():
        for k in keys.split(","):
            outputs[k] = val
    return outputs


@typechecked
def pdb_parser(path: Union[str, pathlib.Path]):
    """
    Parse .pdb or .pdb.gz
    :param path: 
    :return: (gemmi.Structure, entity)
    """
    if _is_pdb(path):
        struct = gemmi.read_structure(str(path))
        struct.resolution = _get_pdb_resolution(struct.raw_remarks)
        ent_0 = _pdb_entity_info(path)
        ch2desc = _melt_dict(ent_0.eid2desc)
        ch2specie = _melt_dict(ent_0.eid2specie)
        ch2taxid = _melt_dict(ent_0.eid2taxid)

        struct.setup_entities()
        block = struct.make_mmcif_block()
        ent_t = _cif_entity_info(block)

        # set non-polymer entity names
        non_polymer_entities = [e.name for e in struct.entities if e.polymer_type.name == "Unknown"]
        for k in non_polymer_entities:
            assert k in ent_t.eid2desc
            if ent_t.eid2desc[k] == "?":
                ent_t.eid2desc[k] = k

        for k in ent_t.eid2desc.keys():
            if k not in non_polymer_entities:
                ent_t.eid2desc[k] = ch2desc.get(k, "?")

        polymer_chs_used_as_eid = set(ch2specie.keys()).intersection(ent_t.eid2desc.keys())
        for k in polymer_chs_used_as_eid:
            ent_t.eid2specie[k] = ch2specie.get(k, "?")
            ent_t.eid2taxid[k] = ch2taxid.get(k, "?")

        m = _assign_digital_entity_names(struct)
        _update_entity_names(ent_t, m)

        return struct, ent_t
    else:
        raise ValueError("Only support .pdb or .pdb.gz file, but got %s" % path)


@typechecked
def _chain_type(structure: gemmi.Structure, chain_id: str) -> str:
    out = None
    values = {"PeptideL": "protein",
              "Dna": "dna",
              "Rna": "rna"}

    for model in structure:
        for cur_chain in model:
            if cur_chain.name == chain_id:
                sc_types = set()
                for sc in cur_chain.subchains():
                    t = sc.check_polymer_type().name
                    if t != "Unknown":
                        sc_types.update({t})

                if len(sc_types) == 1:
                    out = sc_types.pop()
                else:
                    out = "Unknown"
    if out is None:
        raise RuntimeError("chain_id %s not in structure" % chain_id)
    else:
        return values.get(out, "other")


@typechecked
def _get_model_chain_names(model: gemmi.Model) -> List[str]:
    vals = []
    for ch in model:
        vals.append(ch.name)
    return vals


@typechecked
def _assert_unique_chain_names_in_models(structure: gemmi.Structure):
    for model in structure:
        names = _get_model_chain_names(model)
        nums = Counter(names)
        dup_names = [k for k, v in nums.items() if v > 1]

        if dup_names:
            raise RuntimeError("Duplicate chain names in model %d: %s" % (model.num, ",".join(dup_names)))


@typechecked
def _chain_names2one_letter(structure: gemmi.Structure, only_uppercase: bool = True) -> Dict[str, str]:
    """
    Automatically generate one letter mapper when the length of chain name > 1 or chain name is not uppercase letters

    (1) when only_uppercase is True, only supported when the number of chains of the one-model structure <= 26
    (2) when only_uppercase is False, only supported when the number of chains of the one-model structure <= 62

    If there are too many chains, make some splits or assemblies first,
    or just keep the longer chain names in .cif format.
    PDB only support the single letter chain name.
    """

    if len(structure) > 1:
        raise RuntimeError("> 1 models in structure, do nothing")

    _assert_unique_chain_names_in_models(structure)

    n_chains = len(structure[0])
    if only_uppercase:
        l1 = ['Z', 'Y', 'X', 'W', 'V', 'U', 'T', 'S', 'R', 'Q', 'P', 'O', 'N', 'M',
              'L', 'K', 'J', 'I', 'H', 'G', 'F', 'E', 'D', 'C', 'B', 'A']
        mode = "UPPERCASE"
    else:
        l1 = ['9', '8', '7', '6', '5', '4', '3', '2', '1', '0',
              'z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q',
              'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g',
              'f', 'e', 'd', 'c', 'b', 'a', 'Z', 'Y', 'X', 'W',
              'V', 'U', 'T', 'S', 'R', 'Q', 'P', 'O', 'N', 'M',
              'L', 'K', 'J', 'I', 'H', 'G', 'F', 'E', 'D', 'C', 'B', 'A']
        mode = "UPPERCASE + LOWERCASE + DIGITAL"

    if n_chains > len(l1):
        raise RuntimeError("Support max %d chains under %s mode, but got %d chains in structure"
                           % (len(l1), mode, n_chains))

    existed_one_letter_ids = []
    for model in structure:
        for chain in model:
            if chain.name in l1 and chain.name not in existed_one_letter_ids:
                existed_one_letter_ids.append(chain.name)

    left_l1 = [i for i in l1 if i not in existed_one_letter_ids]

    name_mapper = dict()
    for model in structure:
        for chain in model:
            if chain.name not in l1:
                new_name = left_l1.pop()
                name_mapper[chain.name] = new_name
    return name_mapper


@typechecked
def get_assembly(structure: gemmi.Structure, assembly_name: str,
                 how: gemmi.HowToNameCopiedChain = gemmi.HowToNameCopiedChain.AddNumber):
    struct = structure.clone()
    struct.transform_to_assembly(assembly_name, how)

    # update ENTITY.polymer2eid
    scn2eid = dict()
    for ent in struct.entities:
        for scn in ent.subchains:
            scn2eid[scn] = ent.name

    polymer2eid = dict()
    for model in struct:
        for chain in model:
            for sc in chain.subchains():
                sc_t = sc.check_polymer_type().name
                if sc_t in ["PeptideL", "Dna", "Rna"]:
                    polymer2eid[chain.name] = scn2eid[sc.subchain_id()]
                    break
    return struct, polymer2eid
