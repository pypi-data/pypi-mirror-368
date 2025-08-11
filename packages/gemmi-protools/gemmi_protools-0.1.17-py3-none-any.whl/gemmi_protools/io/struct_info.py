"""
@Author: Luo Jiejian
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

import gemmi
from typeguard import typechecked


@typechecked
@dataclass
class Entity:
    eid2desc: Dict[str, str] = field(default_factory=dict)
    eid2specie: Dict[str, str] = field(default_factory=dict)
    eid2taxid: Dict[str, str] = field(default_factory=dict)
    polymer2eid: Dict[str, str] = field(default_factory=dict)

    @typechecked
    def __setattr__(self, name: str, value: Dict[str, str]):
        super().__setattr__(name, value)

    @typechecked
    def update(self, inputs: Dict[str, Dict[str, str]]):
        for key, value in inputs.items():
            if hasattr(self, key):
                self.__setattr__(key, value)

    def get(self, name: str, default: Optional[str] = None):
        if hasattr(self, name):
            return self.__getitem__(name)
        else:
            return default

    def __getitem__(self, name: str):
        return getattr(self, name)

    def keys(self):
        return list(self.__dict__.keys())


@typechecked
@dataclass
class Info:
    cell_Z: str = ""
    pdb_id: str = ""
    exp_method: str = ""
    deposition_date: str = "1909-01-08"
    title: str = ""
    keywords: str = ""
    keywords_text: str = ""

    @property
    def __attributes_mapper(self):
        return {'cell_Z': '_cell.Z_PDB',
                'pdb_id': '_entry.id',
                'exp_method': '_exptl.method',
                'deposition_date': '_pdbx_database_status.recvd_initial_deposition_date',
                'title': '_struct.title',
                'keywords': '_struct_keywords.pdbx_keywords',
                'keywords_text': '_struct_keywords.text'}

    def to_gemmi_structure_infomap(self) -> gemmi.InfoMap:
        outputs = dict()
        for name, target_name in self.__attributes_mapper.items():
            value = self.__getattribute__(name)
            if isinstance(value, str):
                v = str(value)
                if len(v) > 1:
                    outputs[target_name] = v
        return gemmi.InfoMap(outputs)

    @typechecked
    def from_gemmi_structure_infomap(self, infomap: gemmi.InfoMap):
        mapper_iv = {v: k for k, v in self.__attributes_mapper.items()}
        for key, val in infomap.items():
            if key in mapper_iv:
                name = mapper_iv[key]
                self.__setattr__(name, val)

    @typechecked
    def __setattr__(self, name: str, value: str):
        if name == "deposition_date":
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError as e:
                raise ValueError(f"{e}")

        if hasattr(self, name):
            super().__setattr__(name, value)
