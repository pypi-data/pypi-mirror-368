import traceback, datetime, json, copy
import urllib.parse
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config
import adagenes as ag


class MolecularFeaturesClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines= config.molecular_features_info_lines
        self.url_pattern = config.molecular_features_src
        self.srv_prefix = config.molecular_features_srv_prefix
        self.response_keys = config.molecular_features_response_keys
        self.extract_keys = config.molecular_features_keys

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"
        self.error_logfile = error_logfile

    def process_data(self, biomarker_data, tumor_type=None):
        """

        :param biomarker_data:
        :param tumor_type:
        :return:
        """
        try:
            vcf_linesf = ag.tools.filter_wildtype_variants(biomarker_data)

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

            #print("len vars ",len(list(biomarker_data.keys())))

            for var in qid_list0:
                if retransform is False:
                    var_orig = var
                else:
                    if var in qid_dc:
                        qid_orig = qid_dc[var]
                    else:
                        qid_orig = var
                    var_orig = qid_orig

                if "UTA_Adapter" in biomarker_data[var_orig]:
                    if "gene_name" in biomarker_data[var_orig]["UTA_Adapter"]:
                        genes.append(biomarker_data[var_orig]["UTA_Adapter"]["gene_name"])
                        variants.append(biomarker_data[var_orig]["UTA_Adapter"]["variant_exchange"])
                        qid_list.append(var)
                    else:
                        pass
                elif "UTA_Adapter_gene_name" in biomarker_data[var_orig].keys():
                    genes.append(biomarker_data[var_orig]["UTA_Adapter_gene_name"])
                    variants.append(biomarker_data[var_orig]["UTA_Adapter_variant_exchange"])
                    qid_list.append(var)
                elif "hgnc_gene_symbol" in biomarker_data[var_orig].keys():
                    genes.append(biomarker_data[var_orig]["hgnc_gene_symbol"])
                    variants.append(biomarker_data[var_orig]["aa_exchange"])
                    qid_list.append(var)
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
                            qid_list.append(var)
                        except:
                            print(traceback.format_exc())
                    #else:
                    #    print("hmm ",biomarker_data[var_orig])
                #else:
                #    print("HMM","keys ",biomarker_data[var])

            variants_enc = []
            for var in variants:
                #var_encoded = urllib.parse.quote(var, safe='=&')
                var_encoded = urllib.parse.quote(var)
                variants_enc.append(var_encoded)
            variants = variants_enc
            #print("variants ", len(variants),variants)

            qid_lists_query = ag.tools.split_list(qid_list)
            genes_lists_query = ag.tools.split_list(genes)
            variants_lists_query = ag.tools.split_list(variants)

            for qlist, glist, vlist in zip(qid_lists_query, genes_lists_query, variants_lists_query):
                q_genes = ",".join(glist)
                q_variants = ",".join(vlist)
                q_genompos = ",".join(qlist)
                q = "?genompos=" + q_genompos + "&gene=" + q_genes + "&variant=" + q_variants

                res = req.get_connection(q, self.url_pattern, self.genome_version)

                for var in res.keys():
                    if isinstance(res[var], dict):
                        if "molecular_features" in res[var]:
                            if retransform is False:
                                #biomarker_data[var]["molecular_features"] = res[var]["molecular_features"]
                                biomarker_data[var][self.srv_prefix] = res[var]["molecular_features"]
                            else:
                                qid_orig = qid_dc[var]
                                biomarker_data[qid_orig][self.srv_prefix] = res[var]["molecular_features"]

        except:
            if self.error_logfile is not None:
                cur_dt = datetime.datetime.now()
                date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                print("error processing request: ", biomarker_data, file=self.error_logfile+str(date_time)+'.log')
            else:
                print(": error processing variant response: ;", traceback.format_exc())

        return biomarker_data
