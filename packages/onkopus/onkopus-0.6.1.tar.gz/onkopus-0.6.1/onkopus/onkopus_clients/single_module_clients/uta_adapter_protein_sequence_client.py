import traceback, copy
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config
import adagenes as ag
import onkopus as op


class UTAAdapterProteinSequenceClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines = config.uta_adapter_protein_sequence_info_lines
        self.url_pattern = config.uta_adapter_protein_sequence_src
        self.srv_prefix = config.uta_adapter_protein_sequence_srv_prefix
        self.genomic_keys = config.uta_genomic_keys
        self.gene_keys = config.uta_gene_keys
        self.gene_response_keys = config.uta_gene_response_keys
        self.extract_keys = config.uta_adapter_protein_sequence_keys

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"

    def process_data(self, data, gene_request=False):
        vcf_linesf = ag.tools.filter_wildtype_variants(data)

        retransform = False
        if self.genome_version == "hg38":
            qid_list0 = copy.deepcopy(list(vcf_linesf.keys()))
        else:
            qid_dc, qid_list0 = ag.tools.generate_qid_list_from_other_reference_genome(vcf_linesf)
            self.genome_version = "hg38"
            retransform = True

        qid_list = []
        genes = []
        variants = []
        qid_gene_name_dc = {}
        qid_list = []
        for var in qid_list0:
            if retransform is False:
                var_orig = var
            else:
                qid_orig = qid_dc[var]
                var_orig = qid_orig

            if "UTA_Adapter" in data[var_orig]:
                if "gene_name" in data[var_orig]["UTA_Adapter"]:
                    genes.append(data[var_orig]["UTA_Adapter"]["gene_name"])
                    variants.append(data[var_orig]["UTA_Adapter"]["variant_exchange"])
                    #qid_list.append(var)
                    qid_gene_name_dc[data[var_orig]["UTA_Adapter"]["gene_name"] + ':' + data[var_orig]["UTA_Adapter"][
                        "variant_exchange"]] = [var]
                    qid_list.append(data[var_orig]["UTA_Adapter"]["gene_name"] + ':' + data[var_orig]["UTA_Adapter"][
                        "variant_exchange"])
                else:
                    pass
            elif "UTA_Adapter_gene_name" in data[var_orig].keys():
                genes.append(data[var_orig]["UTA_Adapter_gene_name"])
                variants.append(data[var_orig]["UTA_Adapter_variant_exchange"])
                #qid_list.append(var)
                qid_gene_name_dc[data[var_orig]["UTA_Adapter_gene_name"] + ':' + data[var_orig]["UTA_Adapter_variant_exchange"]] = [var]
                qid_list.append(data[var_orig]["UTA_Adapter_gene_name"] + ':' + data[var_orig]["UTA_Adapter_variant_exchange"])
            elif "hgnc_gene_symbol" in data[var_orig].keys():
                genes.append(data[var_orig]["hgnc_gene_symbol"])
                variants.append(data[var_orig]["aa_exchange"])
                #qid_list.append(var)
                qid_gene_name_dc[data[var_orig]["hgnc_gene_symbol"] + ':' + data[var_orig]["aa_exchange"]] = [var]
                qid_list.append(data[var_orig]["hgnc_gene_symbol"] + ':' + data[var_orig]["aa_exchange"])
            # elif "INFO" in data[var].keys():
            #    pass
            elif "info_features" in data[var_orig].keys():
                # print("INFO ok")
                # print(data[var]["info_features"])
                if "UTA_Adapter_gene_name" in data[var_orig]["info_features"]:
                    genes.append(data[var_orig]["info_features"]["UTA_Adapter_gene_name"])
                    variants.append(data[var_orig]["info_features"]["UTA_Adapter_variant_exchange"])
                    #qid_list.append(var)
                    qid_gene_name_dc[data[var_orig]["info_features"]["UTA_Adapter_gene_name"] + ':' + data[var_orig]["info_features"]["UTA_Adapter_variant_exchange"]] = [var]
                    qid_list.append(data[var_orig]["info_features"]["UTA_Adapter_gene_name"] + ':' + data[var_orig]["info_features"]["UTA_Adapter_variant_exchange"])
            # else:
            #    print("HMM","keys ",data[var])

        qid_lists_query = ag.tools.split_list(qid_list)
        genes_lists_query = ag.tools.split_list(genes)
        variants_lists_query = ag.tools.split_list(variants)

        for q_list in qid_lists_query:
            q = ",".join(q_list).rstrip(",")


            try:
                json_body = req.get_connection(q, self.url_pattern, self.genome_version)

                for key in json_body[0].keys():
                        if gene_request is False:
                            if str(json_body[0][key]["header"]["qid"]) in qid_gene_name_dc.keys():
                                qid = qid_gene_name_dc[str(json_body[0][key]["header"]["qid"])]
                        else:
                            #qid_index = q_list.index(str(json_body[0][key]["header"]["qid"]))
                            #qid = qids_partial[qid_index]
                            qid = str(json_body[0][key]["header"]["qid"])
                            qid = qid_gene_name_dc[qid]
                            #print("genompos for ",str(json_body[0][key]["header"]["qid"]),": ",qid)

                        if json_body[0][key]["data"] is not None:
                            if type(json_body[0][key]["data"]) is dict:
                                #print("available qids: ",list(vcf_lines.keys()))
                                #print(type(qid),",",qid)
                                if isinstance(qid, str):
                                    if retransform is False:
                                        data[qid][self.srv_prefix] = json_body[0][key]["data"]
                                    else:
                                        qid_orig = qid_dc[qid]
                                        data[qid_orig][self.srv_prefix] = json_body[0][key]["data"]
                                elif isinstance(qid, list):
                                    for q in qid:
                                        if retransform is False:
                                            data[q][self.srv_prefix] = json_body[0][key]["data"]
                                        else:
                                            qid_orig = qid_dc[q]
                                            data[qid_orig][self.srv_prefix] = json_body[0][key]["data"]
                            else:
                                data[qid][self.srv_prefix] = {}
                                data[qid][self.srv_prefix]["status"] = 400
                                data[qid][self.srv_prefix]["msg"] = json_body[0][key]["data"]
            except:
                print("error: genomic to gene")
                print(traceback.format_exc())

        return data
