import traceback, datetime, json, copy
from onkopus.conf import read_config as conf_reader
import requests
from json import JSONDecodeError
import adagenes as ag


class GeneExpressionClient:

    def __init__(self, error_logfile=None):
        #self.genome_version = genome_version
        self.info_lines= conf_reader.ge_module_info_lines
        self.url_pattern = conf_reader.ge_module_src
        self.srv_prefix = conf_reader.ge_module_srv_prefix
        self.response_keys = conf_reader.ge_module_response_keys
        self.extract_keys = conf_reader.ge_module_keys

        self.qid_key = "q_id"
        self.error_logfile = error_logfile

    def process_data(self, variant_data):
            """
            Generates JSON data for a Plotly variant needleplot with added variant annotations

            :param variant_data:
            :return:
            """
            vcf_linesf = ag.tools.filter_wildtype_variants(variant_data)

            qid_list0 = copy.deepcopy(list(vcf_linesf.keys()))

            qid_gene_mapping = {}
            qid_list = []
            genes = []
            variants = []
            for var in qid_list0:
                var_orig = var

                if "UTA_Adapter" in variant_data[var_orig]:
                    if "gene_name" in variant_data[var_orig]["UTA_Adapter"]:
                        gene = variant_data[var_orig]["UTA_Adapter"]["gene_name"]
                        genes.append(variant_data[var_orig]["UTA_Adapter"]["gene_name"])
                        variants.append(variant_data[var_orig]["UTA_Adapter"]["variant_exchange"])
                        qid_list.append(var)

                        if gene not in qid_gene_mapping.keys():
                            qid_gene_mapping[gene] = []
                        qid_gene_mapping[gene].append(var_orig)
                    else:
                        pass
                elif "UTA_Adapter_gene_name" in variant_data[var_orig].keys():
                    genes.append(variant_data[var_orig]["UTA_Adapter_gene_name"])
                    variants.append(variant_data[var_orig]["UTA_Adapter_variant_exchange"])
                    qid_list.append(var)
                    gene = variant_data[var_orig]["UTA_Adapter_gene_name"]
                    if gene not in qid_gene_mapping.keys():
                        qid_gene_mapping[gene] = []
                    qid_gene_mapping[gene].append(var_orig)
                elif "hgnc_gene_symbol" in variant_data[var_orig].keys():
                    genes.append(variant_data[var_orig]["hgnc_gene_symbol"])
                    variants.append(variant_data[var_orig]["aa_exchange"])
                    qid_list.append(var)
                    gene = variant_data[var_orig]["hgnc_gene_symbol"]
                    if gene not in qid_gene_mapping.keys():
                        qid_gene_mapping[gene] = []
                    qid_gene_mapping[gene].append(var_orig)
                # elif "INFO" in variant_data[var].keys():
                #    pass
                elif "info_features" in variant_data[var_orig].keys():
                    # print("INFO ok")
                    # print(variant_data[var]["info_features"])
                    if "UTA_Adapter_gene_name" in variant_data[var_orig]["info_features"]:
                        genes.append(variant_data[var_orig]["info_features"]["UTA_Adapter_gene_name"])
                        variants.append(variant_data[var_orig]["info_features"]["UTA_Adapter_variant_exchange"])
                        qid_list.append(var)
                        gene = variant_data[var_orig]["info_features"]["UTA_Adapter_gene_name"]
                        if gene not in qid_gene_mapping.keys():
                            qid_gene_mapping[gene] = []
                        qid_gene_mapping[gene].append(var_orig)
                elif "mutation_type" in variant_data[var]:
                    if variant_data[var_orig]["mutation_type"] == "gene":
                        qid_list.append(var)
                        genes.append("")
                        variants.append("")

                        if var not in qid_gene_mapping.keys():
                            qid_gene_mapping[var_orig] = []
                        qid_gene_mapping[var_orig].append(var)

            
            #qid_gene_mapping = {}
            #qid_list = []
            #for var in variant_data.keys():
            #    if "UTA_Adapter" in variant_data[var]:
            #        if ("gene_name" in variant_data[var]["UTA_Adapter"]):
            #            qid_list.append(variant_data[var]["UTA_Adapter"]["gene_name"])
            #            if variant_data[var]["UTA_Adapter"]["gene_name"] not in qid_gene_mapping.keys():
            #                qid_gene_mapping[variant_data[var]["UTA_Adapter"]["gene_name"]] = []

            #            qid_gene_mapping[variant_data[var]["UTA_Adapter"]["gene_name"]].append(var)
            #    elif "mutation_type" in variant_data[var]:
            #        if variant_data[var]["mutation_type"] == "gene":
            #            qid_list.append(var)

            #            if var not in qid_gene_mapping.keys():
            #                qid_gene_mapping[var] = []
            #            qid_gene_mapping[var].append(var)

            #qid_lists_query = ag.tools.split_list(qid_list)
            qid_lists_query = ag.tools.split_list(qid_list)
            genes_lists_query = ag.tools.split_list(genes)
            variants_lists_query = ag.tools.split_list(variants)

            for i,qid_list in enumerate(qid_lists_query):
                gene_list = genes_lists_query[i]
                url = conf_reader.ge_module_src + "?gene=" + ",".join(gene_list).rstrip(",")
                print(url)
                json_body = (requests.get(url, timeout=60))
                json_body = json_body.json()
                try:
                    for gene in json_body.keys():
                        if gene != "":
                            for associated_var in qid_gene_mapping[gene]:
                                variant_data[associated_var]["gtex"] = json_body[gene][0]
                except:
                    print(traceback.format_exc())

            return variant_data
