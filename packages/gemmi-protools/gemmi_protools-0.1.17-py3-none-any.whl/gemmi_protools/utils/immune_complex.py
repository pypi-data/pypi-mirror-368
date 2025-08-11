"""
@Author: Luo Jiejian
"""
from collections import defaultdict
from copy import deepcopy

from gemmi_protools import StructureParser
from gemmi_protools.utils.pdb_annot import hash_sequence, annotate_pdb


class ImmuneComplex(object):
    def __init__(self, annotation: dict,
                 min_ppi_res_hl=8,
                 min_ppi_res_hl_a=4,
                 min_ppi_res_mhc1_globulin=10,
                 min_ppi_res_mhc2_ab=20):
        """

        Args:
            annotation: output from pdb_annot.annotate_pdb
            min_ppi_res_hl: min PPI (H-L) res, default 8
            min_ppi_res_hl_a: min PPI (HL-antigen) res on antigen, default 4
            min_ppi_res_mhc1_globulin: min PPI (MHC I - globulin) res on globulin, default 10
            min_ppi_res_mhc2_ab: min PPI (MHC II alpha - MHC II beta) res on MHC II alpha or MHC II beta, default 20
        """
        self.annotation = annotation
        self.min_ppi_res_hl = min_ppi_res_hl
        self.min_ppi_res_hl_a = min_ppi_res_hl_a
        self.min_ppi_res_mhc1_globulin = min_ppi_res_mhc1_globulin
        self.min_ppi_res_mhc2_ab = min_ppi_res_mhc2_ab
        self.ch_infos = self._get_chain_infos()
        self.ig_hl_pairs, self.vhh_chains = self._get_ig_hl_pairs()
        self.tr_hl_pairs = self._get_tr_hl_pairs()

        self.load_assembly_info()

    def load_assembly_info(self):
        st = StructureParser()
        st.load_from_file(self.annotation["path"])
        st.set_default_model()
        st.STRUCT.remove_alternative_conformations()
        st.STRUCT.remove_ligands_and_waters()
        st.STRUCT.remove_hydrogens()
        st.STRUCT.remove_empty_chains()
        st.update_entity()

        original_keys = set(self.ch_infos["ch2hash_id"].items())

        try:
            values = dict()
            key_records = set()
            for name in st.assembly_names:
                assem = st.get_assembly(name)
                cur_keys = {(ch, hash_sequence(seq)) for ch, seq in assem.polymer_sequences.items()}

                if cur_keys.issubset(original_keys):
                    key_records.update(cur_keys)

                    cur_chs = list(assem.polymer_sequences.keys())
                    cur_chs.sort()

                    values[name] = cur_chs

            if key_records == original_keys:
                full_coverage = True
            else:
                full_coverage = False
        except Exception as e:
            values = dict()
            full_coverage = False

        self.annotation["assembly"] = dict(assem_name2ch=values, full_coverage=full_coverage)

    def _get_chain_infos(self):
        immune_dict = defaultdict(list)
        antigens = []
        seq_lens = dict()
        mhc_dict = defaultdict(list)
        immune_hash_set = []

        for val in self.annotation["polymers"].values():
            n = len(val["sequence"])
            for ch in val["chain_ids"]:
                seq_lens[ch] = n

        for hash_id, ann_val in self.annotation["anarci"].items():
            fv_type = ann_val["fv_type"]
            chs = self.annotation["polymers"][hash_id]["chain_ids"]

            if fv_type in ["IG/VL", "IG/VH", "IG/scFv", "TR/VL", "TR/VH", "TR/scFv"]:
                immune_dict[fv_type].extend(chs)

            immune_hash_set.append(hash_id)

        for hash_id, mhc_type in self.annotation["mhc"].items():
            chs = self.annotation["polymers"][hash_id]["chain_ids"]
            mhc_dict[mhc_type].extend(chs)

        for hash_id, seq in self.annotation["polymers"].items():
            if hash_id not in immune_hash_set and seq["type"] == "protein":
                antigens.extend(seq["chain_ids"])

        ch2mhc_type = dict()

        for t, chs in mhc_dict.items():
            for ch in chs:
                ch2mhc_type[ch] = t

        ch2hash_id = dict()
        for hash_id, val in self.annotation["polymers"].items():
            for ch in val["chain_ids"]:
                ch2hash_id[ch] = hash_id

        return dict(antigens=antigens,
                    immune={k: v for k, v in immune_dict.items()},
                    mhc_type2ch={k: v for k, v in mhc_dict.items()},
                    ch2mhc_type=ch2mhc_type,
                    seq_lens=seq_lens,
                    ch2hash_id=ch2hash_id,
                    )

    def _get_antigen_ppi_res(self, query_ch: str, query_antigen: str):
        """

        Args:
            query_ch: str, chain id
            query_antigen: str, chain id

        Returns:

        """

        if query_antigen > query_ch:
            ag_idx = 1
            key = "%s/%s" % (query_ch, query_antigen)
        else:
            ag_idx = 0
            key = "%s/%s" % (query_antigen, query_ch)

        if key in self.annotation["interfaces"]:
            return self.annotation["interfaces"][key][ag_idx]
        else:
            return []

    def _find_globulin(self, ch_mhc_i):
        tmp = []
        for ch in self.ch_infos["antigens"]:
            if ch not in self.ch_infos["ch2mhc_type"]:
                res = self._get_antigen_ppi_res(ch_mhc_i, ch)
                if len(res) >= self.min_ppi_res_mhc1_globulin:
                    tmp.append((len(res), ch))
        tmp.sort(reverse=True)
        if len(tmp) > 0:
            return tmp[0][1]
        else:
            return ""

    def _find_mhc_chain_with_most_ppi_res(self, immune_chains):
        """
        # No Ok for all instances, not Use
        # outlier: 2ak4, 5ksb
        Args:
            immune_chains:

        Returns:

        """

        tmp = []
        for mhc_type, mhc_chains in self.ch_infos["mhc_type2ch"].items():
            for ch_mhc in mhc_chains:
                res = set()
                for ch in immune_chains:
                    res.update(self._get_antigen_ppi_res(ch, ch_mhc))

                if len(res) >= self.min_ppi_res_hl_a:
                    tmp.append((len(res), ch_mhc, mhc_type))

        tmp.sort(reverse=True)

        if len(tmp) > 0:
            return tmp[0][1], tmp[0][2]
        else:
            return None

    def _find_mhc_peptide(self, mhc_chains):
        tmp = []
        for ch in self.ch_infos["antigens"]:
            if ch not in self.ch_infos["ch2mhc_type"] and self.ch_infos["seq_lens"][ch] < 30:
                res_2 = set()
                for q_ch in mhc_chains:
                    res_2.update(self._get_antigen_ppi_res(q_ch, ch))

                if len(res_2) >= self.min_ppi_res_hl_a:
                    tmp.append((len(res_2), ch))

        tmp.sort(reverse=True)
        if len(tmp) > 0:
            return tmp[0][1]
        else:
            return ""

    def search_complex_for_IG_scFv(self):
        results = []
        if "IG/scFv" in self.ch_infos["immune"]:
            for ch in self.ch_infos["immune"]["IG/scFv"]:
                records = []
                n_ppi_ag_res = 0
                for ag in self.ch_infos["antigens"]:
                    res = self._get_antigen_ppi_res(ch, ag)
                    if len(res) >= self.min_ppi_res_hl_a:
                        records.append(ag)
                        n_ppi_ag_res += len(res)

                if len(records) > 0:
                    records.sort()
                    results.append(dict(immune_type="IGscFv",
                                        chain_H=ch,
                                        chain_L="",
                                        ch_antigens=records,
                                        n_ppi_ag_res=n_ppi_ag_res)
                                   )
        return results

    def search_complex_for_TR_scFv(self):
        results = []
        if "TR/scFv" in self.ch_infos["immune"]:
            for ch in self.ch_infos["immune"]["TR/scFv"]:
                records = []
                n_ppi_ag_res = 0
                for ag in self.ch_infos["antigens"]:
                    res = self._get_antigen_ppi_res(ch, ag)
                    if len(res) >= self.min_ppi_res_hl_a:
                        records.append(ag)
                        n_ppi_ag_res += len(res)

                if len(records) > 0:
                    records.sort()
                    results.append(dict(immune_type="TRscFv",
                                        chain_H=ch,
                                        chain_L="",
                                        ch_antigens=records,
                                        n_ppi_ag_res=n_ppi_ag_res)
                                   )
        return results

    def _get_ig_hl_pairs(self):
        """

        Returns:
            a tuple (HL pairs, VHH chains)
            HL pairs: list of tuple of (VH, VL)
            VHH chains: list of chains
        """
        hl_pairs = []
        vhh_chains = []

        matched_h_chains = []
        if "IG/VH" in self.ch_infos["immune"]:
            for ch_vh in self.ch_infos["immune"]["IG/VH"]:
                if "IG/VL" in self.ch_infos["immune"]:
                    tmp_pairs = []

                    for ch_vl in self.ch_infos["immune"]["IG/VL"]:
                        if ch_vh > ch_vl:
                            key = "%s/%s" % (ch_vl, ch_vh)
                        else:
                            key = "%s/%s" % (ch_vh, ch_vl)

                        if key in self.annotation["interfaces"]:
                            ppi_res_hl = len(self.annotation["interfaces"][key][0]) + len(
                                self.annotation["interfaces"][key][1])
                            if ppi_res_hl >= self.min_ppi_res_hl:
                                tmp_pairs.append((ppi_res_hl, ch_vh, ch_vl))

                    tmp_pairs.sort(reverse=True)
                    if len(tmp_pairs) > 0:
                        hl_pairs.append((tmp_pairs[0][1], tmp_pairs[0][2]))
                        matched_h_chains.append(tmp_pairs[0][1])

            vhh_chains = [ch_vh for ch_vh in self.ch_infos["immune"]["IG/VH"] if ch_vh not in matched_h_chains]
        return hl_pairs, vhh_chains

    def _get_tr_hl_pairs(self):
        """

        Returns:
            TR HL pairs, list of (VH, VL)
        """
        hl_pairs = []
        if "TR/VH" in self.ch_infos["immune"]:
            for ch_vh in self.ch_infos["immune"]["TR/VH"]:
                if "TR/VL" in self.ch_infos["immune"]:
                    tmp_pairs = []

                    for ch_vl in self.ch_infos["immune"]["TR/VL"]:
                        if ch_vh > ch_vl:
                            key = "%s/%s" % (ch_vl, ch_vh)
                        else:
                            key = "%s/%s" % (ch_vh, ch_vl)

                        if key in self.annotation["interfaces"]:
                            ppi_res_hl = len(self.annotation["interfaces"][key][0]) + len(
                                self.annotation["interfaces"][key][1])
                            if ppi_res_hl >= self.min_ppi_res_hl:
                                tmp_pairs.append((ppi_res_hl, ch_vh, ch_vl))

                    tmp_pairs.sort(reverse=True)
                    if len(tmp_pairs) > 0:
                        hl_pairs.append((tmp_pairs[0][1], tmp_pairs[0][2]))
        return hl_pairs

    def search_complex_for_IG_HL(self):
        results = []
        for ch_vh, ch_vl in self.ig_hl_pairs:
            records = []
            n_ppi_ag_res = 0
            for ag in self.ch_infos["antigens"]:
                res_h = self._get_antigen_ppi_res(ch_vh, ag)
                res_l = self._get_antigen_ppi_res(ch_vl, ag)
                _n = len(set(res_h + res_l))
                if _n >= self.min_ppi_res_hl_a:
                    records.append(ag)
                    n_ppi_ag_res += _n

            if len(records) > 0:
                records.sort()
                results.append(dict(immune_type="IG",
                                    chain_H=ch_vh,
                                    chain_L=ch_vl,
                                    ch_antigens=records,
                                    n_ppi_ag_res=n_ppi_ag_res)
                               )
        return results

    def search_complex_for_VHH(self):
        results = []
        for ch_vh in self.vhh_chains:
            records = []
            n_ppi_ag_res = 0
            for ag in self.ch_infos["antigens"]:
                res_h = self._get_antigen_ppi_res(ch_vh, ag)
                _n = len(res_h)
                if _n >= self.min_ppi_res_hl_a:
                    records.append(ag)
                    n_ppi_ag_res += _n

            if len(records) > 0:
                records.sort()
                results.append(dict(immune_type="VHH",
                                    chain_H=ch_vh,
                                    chain_L="",
                                    ch_antigens=records,
                                    n_ppi_ag_res=n_ppi_ag_res)
                               )
        return results

    def search_complex_for_TR_HL(self):
        results = []
        for ch_vh, ch_vl in self.tr_hl_pairs:
            records = []
            n_ppi_ag_res = 0
            for ag in self.ch_infos["antigens"]:
                res_h = self._get_antigen_ppi_res(ch_vh, ag)
                res_l = self._get_antigen_ppi_res(ch_vl, ag)
                _n = len(set(res_h + res_l))
                if _n >= self.min_ppi_res_hl_a:
                    records.append(ag)
                    n_ppi_ag_res += _n

            if len(records) > 0:
                records.sort()
                results.append(dict(immune_type="TR",
                                    chain_H=ch_vh,
                                    chain_L=ch_vl,
                                    ch_antigens=records,
                                    n_ppi_ag_res=n_ppi_ag_res)
                               )
        return results

    def _update_antigen_ppi_res(self, query_chains, antigen_chains):
        res = set()
        for q_ch in query_chains:
            for q_ag in antigen_chains:
                res.update(self._get_antigen_ppi_res(q_ch, q_ag))
        return len(res)

    def _double_check_with_assembly(self, item):
        """

        Args:
            item: element from .run

        Returns:

        """

        if item["chain_L"] == "":
            immune_chains = {item["chain_H"]}
        else:
            immune_chains = {item["chain_H"], item["chain_L"]}

        tmp = []
        for assem_name, assem_chs in self.annotation["assembly"]["assem_name2ch"].items():
            s0 = set(assem_chs)
            if immune_chains.issubset(s0):
                ch_antigens = set(item["ch_antigens"])
                ch_diff = ch_antigens - s0
                tmp.append((len(ch_diff), len(s0), ch_antigens.intersection(s0)))

        tmp.sort(reverse=False)
        if len(tmp) > 0:
            n_diff, _, common_ags = tmp[0]
            if n_diff > 0 and len(common_ags) > 0:
                new_ag_chs = list(common_ags)
                new_ag_chs.sort()

                n_ppi_ag_res = self._update_antigen_ppi_res(list(immune_chains),
                                                            antigen_chains=new_ag_chs)
                item["ch_antigens"] = new_ag_chs
                item["n_ppi_ag_res"] = n_ppi_ag_res
                return item
            else:
                return item
        else:
            return item

    def run(self):
        results = []
        results.extend(self.search_complex_for_IG_HL())
        results.extend(self.search_complex_for_TR_HL())
        results.extend(self.search_complex_for_VHH())
        results.extend(self.search_complex_for_IG_scFv())
        results.extend(self.search_complex_for_TR_scFv())

        # Refine with assembly, if full_coverage is True
        # check MHC antigens
        check_results = []
        for org_item in results:
            item = self._double_check_with_assembly(org_item)
            cts = defaultdict(list)
            for ag in item["ch_antigens"]:
                if ag in self.ch_infos["ch2mhc_type"]:
                    t = self.ch_infos["ch2mhc_type"][ag]
                    cts[t].append(ag)

            uniq_types = set(cts.keys())

            if item["chain_L"] == "":
                immune_chains = [item["chain_H"]]
            else:
                immune_chains = [item["chain_H"], item["chain_L"]]

            if len(cts) == 0:
                item["ch_antigens"] = "/".join(item["ch_antigens"])
                item["check_status"] = "Y"
                item["mhc_type_of_antigen"] = ""
                check_results.append(item)
            else:
                # chain order
                # MHC I / globulin / peptide
                # MHC II alpha / MHC II beta / peptide

                if uniq_types == {"MHC_I"}:
                    if len(cts["MHC_I"]) == 1:
                        # Find pair globulin
                        mhc_chain = cts["MHC_I"][0]
                        ch_globulin = self._find_globulin(mhc_chain)
                        peptide = self._find_mhc_peptide(mhc_chains=[mhc_chain])
                        item["ch_antigens"] = "/".join([mhc_chain, ch_globulin, peptide])
                        item["check_status"] = "Y"

                        if peptide != "":
                            ag_chs = [mhc_chain, peptide]
                        else:
                            ag_chs = [mhc_chain]
                        n_ppi_ag_res = self._update_antigen_ppi_res(immune_chains,
                                                                    antigen_chains=ag_chs)
                        item["n_ppi_ag_res"] = n_ppi_ag_res
                        item["mhc_type_of_antigen"] = "MHC I"
                        check_results.append(item)
                    else:
                        is_fixed = False
                        for mhc_chain in cts["MHC_I"]:
                            peptide = self._find_mhc_peptide(mhc_chains=[mhc_chain])
                            if peptide in item["ch_antigens"]:
                                ch_globulin = self._find_globulin(mhc_chain)

                                item["ch_antigens"] = "/".join([mhc_chain, ch_globulin, peptide])
                                item["check_status"] = "Y"

                                n_ppi_ag_res = self._update_antigen_ppi_res(immune_chains,
                                                                            antigen_chains=[mhc_chain, peptide])
                                item["n_ppi_ag_res"] = n_ppi_ag_res
                                item["mhc_type_of_antigen"] = "MHC I"
                                check_results.append(item)
                                is_fixed = True
                                break

                        if not is_fixed:
                            item["ch_antigens"] = "/".join(item["ch_antigens"])
                            item["check_status"] = "N"
                            item["mhc_type_of_antigen"] = ""
                            check_results.append(item)

                elif uniq_types.issubset({"MHC_II_alpha", "MHC_II_beta"}):
                    if len(cts["MHC_II_alpha"]) == 1 and len(cts["MHC_II_beta"]) == 1:
                        alpha = cts["MHC_II_alpha"][0]
                        beta = cts["MHC_II_beta"][0]

                        peptide = self._find_mhc_peptide(mhc_chains=[alpha, beta])
                        item["ch_antigens"] = "/".join([alpha, beta, peptide])
                        item["check_status"] = "Y"

                        if peptide != "":
                            ag_chs = [alpha, beta, peptide]
                        else:
                            ag_chs = [alpha, beta]
                        n_ppi_ag_res = self._update_antigen_ppi_res(immune_chains,
                                                                    antigen_chains=ag_chs)
                        item["n_ppi_ag_res"] = n_ppi_ag_res
                        item["mhc_type_of_antigen"] = "MHC II"
                        check_results.append(item)
                    else:
                        if len(cts["MHC_II_alpha"]) == 1 and len(cts["MHC_II_beta"]) > 1:
                            alpha = cts["MHC_II_alpha"][0]
                            beta = ""

                            for q_beta in cts["MHC_II_beta"]:
                                res = self._get_antigen_ppi_res(q_beta, alpha)
                                if len(res) >= self.min_ppi_res_mhc2_ab:
                                    # Found
                                    beta = q_beta
                                    break

                        elif len(cts["MHC_II_alpha"]) > 1 and len(cts["MHC_II_beta"]) == 1:
                            beta = cts["MHC_II_beta"][0]
                            alpha = ""

                            for q_alpha in cts["MHC_II_alpha"]:
                                res = self._get_antigen_ppi_res(q_alpha, beta)
                                if len(res) >= self.min_ppi_res_mhc2_ab:
                                    # Found
                                    alpha = q_alpha
                                    break
                        elif len(cts["MHC_II_alpha"]) == 1 and len(cts["MHC_II_beta"]) == 0:
                            # due to IG or TR has no interaction with MHC_II_beta
                            # find MHC_II_beta in all MHC_II_beta chains.
                            alpha = cts["MHC_II_alpha"][0]
                            beta = ""

                            for q_beta in self.ch_infos["mhc_type2ch"]["MHC_II_beta"]:
                                res = self._get_antigen_ppi_res(q_beta, alpha)
                                if len(res) >= self.min_ppi_res_mhc2_ab:
                                    # Found
                                    beta = q_beta
                                    break

                        elif len(cts["MHC_II_alpha"]) == 0 and len(cts["MHC_II_beta"]) == 1:
                            # due to IG or TR has no interaction with MHC_II_beta
                            # find MHC_II_beta in all MHC_II_beta chains.
                            alpha = ""
                            beta = cts["MHC_II_beta"][0]

                            for q_alpha in self.ch_infos["mhc_type2ch"]["MHC_II_alpha"]:
                                res = self._get_antigen_ppi_res(q_alpha, beta)
                                if len(res) >= self.min_ppi_res_mhc2_ab:
                                    # Found
                                    alpha = q_alpha
                                    break
                        else:
                            alpha = ""
                            beta = ""

                        if alpha != "" and beta != "":
                            peptide = self._find_mhc_peptide(mhc_chains=[alpha, beta])
                            item["ch_antigens"] = "/".join([alpha, beta, peptide])
                            item["check_status"] = "Y"

                            if peptide != "":
                                ag_chs = [alpha, beta, peptide]
                            else:
                                ag_chs = [alpha, beta]
                            n_ppi_ag_res = self._update_antigen_ppi_res(immune_chains,
                                                                        antigen_chains=ag_chs)
                            item["n_ppi_ag_res"] = n_ppi_ag_res
                            item["mhc_type_of_antigen"] = "MHC II"
                            check_results.append(item)
                        else:
                            item["ch_antigens"] = "/".join(item["ch_antigens"])
                            item["check_status"] = "N"
                            item["mhc_type_of_antigen"] = ""
                            check_results.append(item)

                else:
                    # contain MHC I  and MHC II
                    item["ch_antigens"] = "/".join(item["ch_antigens"])
                    item["check_status"] = "N"
                    item["mhc_type_of_antigen"] = ""
                    check_results.append(item)

        return check_results

    def add_information(self, element: dict):
        """

        Args:
            element: element of output from self.run

        Returns:

        """
        immune_type = element["immune_type"]

        if immune_type in ["IG", "TR"]:
            h_hash_id = self.ch_infos["ch2hash_id"][element["chain_H"]]
            h_vals = self.annotation["polymers"][h_hash_id]
            h_anarci_ann = self.annotation["anarci"][h_hash_id]["annotations"][0]

            l_hash_id = self.ch_infos["ch2hash_id"][element["chain_L"]]
            l_vals = self.annotation["polymers"][l_hash_id]
            l_anarci_ann = self.annotation["anarci"][l_hash_id]["annotations"][0]

            output = dict(seq_H=h_vals["sequence"],
                          specie_H=h_vals["specie"],
                          taxid_H=h_vals["taxid"],
                          seq_L=l_vals["sequence"],
                          specie_L=l_vals["specie"],
                          taxid_L=l_vals["taxid"],
                          VH=h_anarci_ann["Fv_aa"],
                          type_VH=h_anarci_ann["chain_type"],
                          v_gene_VH=h_anarci_ann["v_gene"],
                          j_gene_VH=h_anarci_ann["j_gene"],
                          cdr1_VH=h_anarci_ann["cdr1_aa"],
                          cdr2_VH=h_anarci_ann["cdr2_aa"],
                          cdr3_VH=h_anarci_ann["cdr3_aa"],
                          VL=l_anarci_ann["Fv_aa"],
                          type_VL=l_anarci_ann["chain_type"],
                          v_gene_VL=l_anarci_ann["v_gene"],
                          j_gene_VL=l_anarci_ann["j_gene"],
                          cdr1_VL=l_anarci_ann["cdr1_aa"],
                          cdr2_VL=l_anarci_ann["cdr2_aa"],
                          cdr3_VL=l_anarci_ann["cdr3_aa"],
                          )
        elif immune_type == "VHH":
            h_hash_id = self.ch_infos["ch2hash_id"][element["chain_H"]]
            h_vals = self.annotation["polymers"][h_hash_id]
            h_anarci_ann = self.annotation["anarci"][h_hash_id]["annotations"][0]

            output = dict(seq_H=h_vals["sequence"],
                          specie_H=h_vals["specie"],
                          taxid_H=h_vals["taxid"],
                          seq_L="",
                          specie_L="",
                          taxid_L="",
                          VH=h_anarci_ann["Fv_aa"],
                          type_VH=h_anarci_ann["chain_type"],
                          v_gene_VH=h_anarci_ann["v_gene"],
                          j_gene_VH=h_anarci_ann["j_gene"],
                          cdr1_VH=h_anarci_ann["cdr1_aa"],
                          cdr2_VH=h_anarci_ann["cdr2_aa"],
                          cdr3_VH=h_anarci_ann["cdr3_aa"],
                          VL="",
                          type_VL="",
                          v_gene_VL="",
                          j_gene_VL="",
                          cdr1_VL="",
                          cdr2_VL="",
                          cdr3_VL="",
                          )
        elif immune_type in ["TRscFv", "IGscFv"]:
            # scFv
            h_hash_id = self.ch_infos["ch2hash_id"][element["chain_H"]]
            h_vals = self.annotation["polymers"][h_hash_id]
            anarci_ann_1, anarci_ann_2 = self.annotation["anarci"][h_hash_id]["annotations"]

            # {"IGH", "IGL"}, {"IGH", "IGK"}, {"TRA", "TRB"}, {"TRG", "TRD"}
            key = "%s%s" % (anarci_ann_1["classification"], anarci_ann_1["chain_type"])

            if key in ["IGH", "TRB", "TRD"]:
                vh_ann = anarci_ann_1
                vl_ann = anarci_ann_2
            else:
                vh_ann = anarci_ann_2
                vl_ann = anarci_ann_1

            output = dict(seq_H=h_vals["sequence"],
                          specie_H=h_vals["specie"],
                          taxid_H=h_vals["taxid"],
                          seq_L="",
                          specie_L="",
                          taxid_L="",
                          VH=vh_ann["Fv_aa"],
                          type_VH=vh_ann["chain_type"],
                          v_gene_VH=vh_ann["v_gene"],
                          j_gene_VH=vh_ann["j_gene"],
                          cdr1_VH=vh_ann["cdr1_aa"],
                          cdr2_VH=vh_ann["cdr2_aa"],
                          cdr3_VH=vh_ann["cdr3_aa"],
                          VL=vl_ann["Fv_aa"],
                          type_VL=vl_ann["chain_type"],
                          v_gene_VL=vl_ann["v_gene"],
                          j_gene_VL=vl_ann["j_gene"],
                          cdr1_VL=vl_ann["cdr1_aa"],
                          cdr2_VL=vl_ann["cdr2_aa"],
                          cdr3_VL=vl_ann["cdr3_aa"],
                          )
        else:
            raise RuntimeError("Unknown immune type: %s" % immune_type)

        base_info = dict(path=self.annotation["path"],
                         pdb_id=self.annotation["info"]["pdb_id"],
                         exp_method=self.annotation["info"]["exp_method"],
                         deposition_date=self.annotation["info"]["deposition_date"],
                         resolution=self.annotation["info"]["resolution"],
                         title=self.annotation["info"]["title"],
                         antigen_hash_id=self.get_antigens_hash_id(element["ch_antigens"])
                         )

        merge_out = deepcopy(element)
        merge_out.update(output)
        merge_out.update(base_info)
        return merge_out

    def get_antigens_hash_id(self, antigens: str):
        out = []
        for ch in antigens.split("/"):
            if ch == "":
                out.append("")
            else:
                out.append(self.ch_infos["ch2hash_id"][ch])
        return "/".join(out)

    def get_antigen_seqs(self, hash_ids: set):
        pdb_id = self.annotation["info"]["pdb_id"]
        out = []
        for hash_id in hash_ids:
            vals = self.annotation["polymers"][hash_id]
            out.append(dict(pdb_id=pdb_id,
                            hash_id=hash_id,
                            specie=vals["specie"],
                            description=vals["description"],
                            taxid=vals["taxid"],
                            sequence=vals["sequence"]
                            )
                       )
        return out


def immune_complex_from_pdb(struct_file: str,
                            ppi_threshold: float = 4.5,
                            min_ppi_res_hl: int = 8,
                            min_ppi_res_hl_a: int = 4,
                            min_ppi_res_mhc1_globulin: int = 10,
                            min_ppi_res_mhc2_ab: int = 20,
                            n_cpus: int = 1,
                            max_seqs: int = 100):
    """

    :param struct_file: str
        path of structure file, .pdb, .cif, .pdb.gz, .cif.gz
    :param ppi_threshold: float, default 4.5
        the maximum distance threshold between heavy atoms to identify interactions
    :param min_ppi_res_hl: int, default 8
        the minimum number of interacting residues between H and L chains
    :param min_ppi_res_hl_a: int, default 4
        the minimum number of interacting residues between HL and antigen chain
    :param min_ppi_res_mhc1_globulin: int, default 10
        the minimum number of interacting residues between MHC 1 and beta micro globulin chain
    :param min_ppi_res_mhc2_ab: int, default 20
        the minimum number of interacting residues between MHC 2 and HL chains
    :param n_cpus:
    :param max_seqs:
    :return:
    """

    annotation = annotate_pdb(struct_file, ppi_threshold, n_cpus, max_seqs)
    func = ImmuneComplex(annotation, min_ppi_res_hl=min_ppi_res_hl,
                         min_ppi_res_hl_a=min_ppi_res_hl_a,
                         min_ppi_res_mhc1_globulin=min_ppi_res_mhc1_globulin,
                         min_ppi_res_mhc2_ab=min_ppi_res_mhc2_ab)
    elements = func.run()
    outputs = []
    for element in elements:
        element_extra = func.add_information(element)
        outputs.append(element_extra)
    return outputs
