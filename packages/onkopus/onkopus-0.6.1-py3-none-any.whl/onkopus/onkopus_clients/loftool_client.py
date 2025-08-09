import datetime, traceback, copy
import adagenes.tools.parse_vcf
import adagenes as ag
from onkopus.conf import read_config as config

qid_key = "q_id"
error_logfile=None

class LoFToolClient:
    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines = config.loftool_info_lines
        self.url_pattern = config.loftool_src
        self.srv_prefix = config.loftool_srv_prefix
        self.extract_keys = config.loftool_keys

        self.qid_key = "q_id"
        self.error_logfile = None
        #if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
        #    self.qid_key = "q_id_hg19"

    def process_data(self, vcf_lines, input_format='json'):
        vcf_linesf = ag.tools.filter_wildtype_variants(vcf_lines)

        qid_dc = {}
        if self.genome_version == "hg38":
            qid_list0 = copy.deepcopy(list(vcf_linesf.keys()))
        else:
            qid_dc, qid_list0 = ag.tools.generate_qid_list_from_other_reference_genome(vcf_linesf)
            self.genome_version = "hg38"
            retransform = True
        #qid_dc, qid_list0 = ag.tools.generate_qid_list_from_other_reference_genome(vcf_linesf)
        self.genome_version = "hg38"

        qid_list = []
        genes = []
        variants = []
        for var in qid_list0:
            if var in qid_dc.keys():
                qid_orig = qid_dc[var]
            else:
                qid_orig = var
            #qid_orig = qid_dc[var]
            var_orig = qid_orig

            if "UTA_Adapter" in vcf_lines[var_orig]:
                if "gene_name" in vcf_lines[var_orig]["UTA_Adapter"]:
                    genes.append(vcf_lines[var_orig]["UTA_Adapter"]["gene_name"])
                    variants.append(vcf_lines[var_orig]["UTA_Adapter"]["variant_exchange"])
                    qid_list.append(var)
                else:
                    pass
            elif "UTA_Adapter_gene_name" in vcf_lines[var_orig].keys():
                genes.append(vcf_lines[var_orig]["UTA_Adapter_gene_name"])
                variants.append(vcf_lines[var_orig]["UTA_Adapter_variant_exchange"])
                qid_list.append(var)
            elif "hgnc_gene_symbol" in vcf_lines[var_orig].keys():
                genes.append(vcf_lines[var_orig]["hgnc_gene_symbol"])
                variants.append(vcf_lines[var_orig]["aa_exchange"])
                qid_list.append(var)
            # elif "INFO" in vcf_lines[var].keys():
            #    pass
            elif "info_features" in vcf_lines[var_orig].keys():
                # print("INFO ok")
                # print(vcf_lines[var]["info_features"])
                if "UTA_Adapter_gene_name" in vcf_lines[var_orig]["info_features"]:
                    genes.append(vcf_lines[var_orig]["info_features"]["UTA_Adapter_gene_name"])
                    variants.append(vcf_lines[var_orig]["info_features"]["UTA_Adapter_variant_exchange"])
                    qid_list.append(var)

        qid_lists_query = ag.tools.split_list(qid_list)
        genes_lists_query = ag.tools.split_list(genes)
        variants_lists_query = ag.tools.split_list(variants)

        for qlist, glist, vlist in zip(qid_lists_query, genes_lists_query, variants_lists_query):
            q_genes = ",".join(glist)
            q_variants = ",".join(vlist)
            q_genompos = ",".join(qlist)

            #max_length = int(config.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            #if max_length > len(qid_list):
            #    max_length = len(qid_list)
            #qids_partial = qid_list[0:max_length]
            #qids_partial = adagenes.tools.filter_alternate_alleles(qids_partial)
            #genompos_str = ','.join(qids_partial)
            #gene_names_partial = \
            #    adagenes.tools.parse_vcf.extract_annotations_json_part(vcf_lines, config.uta_adapter_srv_prefix,[config.uta_genomic_keys[0]],
            #                                                         qids_partial)[config.uta_genomic_keys[0]]
            #gene_names_str = ",".join(gene_names_partial)
            #q = 'genesymbol=' + gene_names_str + '&genompos=' + genompos_str
            q = "genompos=" + q_genompos + "&genesymbol=" + q_genes + "&variant=" + q_variants

            vcf_lines = adagenes.processing.parse_http_responses.parse_module_response(q, vcf_lines, self.url_pattern,
                                                                                     self.genome_version,
                                                                                     self.srv_prefix,
                                                                                       qid_dc)

            #for i in range(0,max_length):
            #    #del gene_names[0] #gene_names.remove(qid)
            #    #del variant_exchange[0]  #variant_exchange.remove(qid)
            #    del qid_list[0] # qid_list.remove(qid)
            #if len(qid_list) == 0:
            #    break

        return vcf_lines
