import copy
import traceback, datetime, json
import urllib.parse
import adagenes as ag
from onkopus.conf import read_config as conf_reader
import requests
from json import JSONDecodeError
import onkopus as op


class ProteinDomainCNAClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines= conf_reader.protein_domains_info_lines
        self.url_pattern = conf_reader.protein_domains_src
        self.srv_prefix = conf_reader.protein_domains_srv_prefix
        self.response_keys = conf_reader.protein_domains_response_keys
        self.extract_keys = conf_reader.protein_domains_keys

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"
        self.error_logfile = error_logfile

    def process_data(self, biomarker_data, plot=None):
            """
            Generates JSON data for a Plotly variant needleplot with added variant annotations

            :param variant_data:
            :return:
            """
            qid_gene_name_dc = {}
            qid_list=[]
            #for qid in data.keys():
            #    variant_data = data[qid]
            #    if "UTA_Adapter" in variant_data:
            #        if ("gene_name" in variant_data["UTA_Adapter"]) and ("variant_exchange" in variant_data["UTA_Adapter"]):
            #            qid_gene_name_dc[variant_data["UTA_Adapter"]["gene_name"] + ':' + variant_data["UTA_Adapter"]["variant_exchange"]] = qid
            #            qid_list.append(variant_data["UTA_Adapter"]["gene_name"] + ':' + variant_data["UTA_Adapter"]["variant_exchange"])
            #    else:
            #        #qid_list.append(qid)
            #        #print("ProteinFeatures: Could not find UTA adapter section: ", variant_data)
            #        pass

            #vcf_linesf = ag.tools.filter_wildtype_variants(biomarker_data)
            vcf_linesf = biomarker_data

            qid_dc = {}
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

            genes_cna_dc = {}
            for var in qid_list0:
                if retransform is False:
                    var_orig = var
                else:
                    qid_orig = qid_dc[var]
                    var_orig = qid_orig

                if "gencode_cna" in biomarker_data[var_orig]:
                    if "gene" in biomarker_data[var_orig]["gencode_cna"]:
                        for gene in biomarker_data[var_orig]["gencode_cna"]["gene"]:
                            gene_name = gene[" gene_name"]
                            if gene_name not in genes_cna_dc:
                                genes_cna_dc[gene_name] = []
                            genes_cna_dc[gene_name].append(var)

                            genes.append(gene_name)
                            #variants.append(biomarker_data[var_orig]["UTA_Adapter"]["variant_exchange"])
                            #qid_list.append(var)
                            qid_gene_name_dc[gene_name] = var_orig
                            qid_list.append(gene_name)
                    else:
                        pass
                elif "UTA_Adapter_gene_name" in biomarker_data[var_orig].keys():
                    genes.append(biomarker_data[var_orig]["UTA_Adapter_gene_name"])
                    variants.append(biomarker_data[var_orig]["UTA_Adapter_variant_exchange"])
                    #qid_list.append(var)
                    qid_gene_name_dc[
                        biomarker_data[var_orig]["UTA_Adapter_gene_name"] ] = var_orig
                    qid_list.append(
                        biomarker_data[var_orig]["UTA_Adapter_gene_name"] )
                elif "hgnc_gene_symbol" in biomarker_data[var_orig].keys():
                    genes.append(biomarker_data[var_orig]["hgnc_gene_symbol"])
                    variants.append(biomarker_data[var_orig]["aa_exchange"])
                    #qid_list.append(var)
                    qid_gene_name_dc[
                        biomarker_data[var_orig]["hgnc_gene_symbol"]] = var_orig
                    qid_list.append(
                        biomarker_data[var_orig]["hgnc_gene_symbol"])
                #elif "INFO" in biomarker_data[var].keys():
                #    pass
                elif "info_features" in biomarker_data[var_orig].keys():
                    #print("INFO ok")
                    #print(biomarker_data[var]["info_features"])
                    if (("UTA_Adapter_gene_name" in biomarker_data[var_orig]["info_features"]) and
                            ("UTA_Adapter_variant_exchange" in biomarker_data[var_orig]["info_features"])):
                        try:
                            genes.append(biomarker_data[var_orig]["info_features"]["UTA_Adapter_gene_name"])
                            variants.append(biomarker_data[var_orig]["info_features"]["UTA_Adapter_variant_exchange"])
                            #qid_list.append(var)
                            qid_gene_name_dc[
                                biomarker_data[var_orig]["info_features"]["UTA_Adapter_gene_name"]] = var_orig
                            qid_list.append(
                                biomarker_data[var_orig]["info_features"]["UTA_Adapter_gene_name"])
                        except:
                            print(traceback.format_exc())


            q_lists = list(op.tools.divide_list(copy.deepcopy(qid_list), chunk_size=100))
            #print("pfeatures ",q_lists)

            for q_list in q_lists:

                variants_enc = []
                for var in q_list:
                    # var_encoded = urllib.parse.quote(var, safe='=&')
                    var_encoded = urllib.parse.quote(var)
                    variants_enc.append(var_encoded)
                variants = variants_enc

                #q = ",".join(q_list)
                q = ",".join(variants)

                url = conf_reader.protein_module_domains_src + "/" + q
                print(url)
                try:
                    json_obj = requests.get(url, timeout=60).json()
                    for result in json_obj:
                        if result["data"] is not None:
                            qid = qid_gene_name_dc[result["header"]["qid"]]
                            if self.srv_prefix not in biomarker_data[qid]:
                                biomarker_data[qid][self.srv_prefix] = {}


                            gene = result["header"]["qid"]
                            biomarker_data[qid][self.srv_prefix][gene] = result["data"]
                except JSONDecodeError:
                    print("Could not decode JSON: ",traceback.format_exc())
                except KeyError:
                    print("Could not parse variant: ",traceback.format_exc())

            return biomarker_data
