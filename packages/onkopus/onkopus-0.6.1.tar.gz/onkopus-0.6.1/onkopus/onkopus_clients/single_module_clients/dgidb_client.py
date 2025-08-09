import datetime, traceback, copy
import adagenes.tools
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config
import adagenes as ag
import onkopus as op


class DGIdbClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.url_pattern = config.dgidb_src
        self.srv_prefix = config.dgidb_srv_prefix
        self.extract_keys = config.dgidb_keys
        self.info_lines = config.dgidb_info_lines
        self.error_logfile = error_logfile

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"

    def process_data(self, vcf_linesf, gene_request=False):
        #print("orig ",vcf_linesf.keys())
        vcf_lines = ag.tools.filter_wildtype_variants(vcf_linesf)
        #print("vcflines ",vcf_lines.keys())

        qid_dc = {}
        retransform = False
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
        qid_gene_name_dc = {}
        for var in qid_list0:
            #print("qid0",qid_list0)
            if retransform is True:
                qid_orig = qid_dc[var]
                var_orig = qid_orig
            else:
                qid_orig = var
                var_orig = qid_orig

            if gene_request is False:
                #print(vcf_lines.keys())
                #print("DGBIDB",vcf_lines[var_orig].keys())
                if "UTA_Adapter" in vcf_lines[var_orig]:
                    if "gene_name" in vcf_lines[var_orig]["UTA_Adapter"]:
                        genes.append(vcf_lines[var_orig]["UTA_Adapter"]["gene_name"])
                        variants.append(vcf_lines[var_orig]["UTA_Adapter"]["variant_exchange"])
                        qid_list.append(var)
                        qid_gene_name_dc[vcf_lines[var_orig]["UTA_Adapter"]["gene_name"]] = var_orig
                    else:
                        pass
                elif "UTA_Adapter_gene_name" in vcf_lines[var_orig].keys():
                    genes.append(vcf_lines[var_orig]["UTA_Adapter_gene_name"])
                    variants.append(vcf_lines[var_orig]["UTA_Adapter_variant_exchange"])
                    qid_list.append(var)
                    qid_gene_name_dc[vcf_lines[var_orig]["UTA_Adapter_gene_name"]] = var_orig
                elif "hgnc_gene_symbol" in vcf_lines[var_orig].keys():
                    genes.append(vcf_lines[var_orig]["hgnc_gene_symbol"])
                    variants.append(vcf_lines[var_orig]["aa_exchange"])
                    qid_list.append(var)
                    qid_gene_name_dc[vcf_lines[var_orig]["hgnc_gene_symbol"]] = var_orig
                # elif "INFO" in vcf_lines[var].keys():
                #    pass
                elif "gencode_cna" in vcf_lines[var_orig]:
                    #print("gencode found")
                    #print(vcf_lines[var_orig]["gencode_cna"])
                    affected_genes = vcf_lines[var_orig]["gencode_cna"]["gene"]
                    for gencode_gene in affected_genes:
                        if " gene_name" in gencode_gene:
                            gene_name = gencode_gene[" gene_name"]
                            genes.append(gene_name)
                            variants.append("")
                            qid_list.append(var_orig)
                            qid_gene_name_dc[gene_name] = var_orig
                elif "info_features" in vcf_lines[var_orig].keys():
                    # print("INFO ok")
                    # print(vcf_lines[var]["info_features"])
                    if "UTA_Adapter_gene_name" in vcf_lines[var_orig]["info_features"]:
                        genes.append(vcf_lines[var_orig]["info_features"]["UTA_Adapter_gene_name"])
                        variants.append(vcf_lines[var_orig]["info_features"]["UTA_Adapter_variant_exchange"])
                        qid_list.append(var)
                        qid_gene_name_dc[vcf_lines[var_orig]["info_features"]["UTA_Adapter_gene_name"]] = var_orig
                else:
                    pass
            else:
                genes.append(var)

        qid_lists_query = ag.tools.split_list(qid_list)
        genes_lists_query = ag.tools.split_list(genes)
        variants_lists_query = ag.tools.split_list(variants)

        #print("ALIST ",qid_lists_query)

        for q_list in genes_lists_query:
            q = ",".join(q_list)
            query = 'genes=' + q
            query = '?' + query

            try:
                json_body = req.get_connection(query, self.url_pattern, "hg38")

                for gene_name in json_body.keys():

                        if gene_request is False:
                            qid = qid_gene_name_dc[gene_name]
                        else:
                            qid = gene_name

                        try:
                            vcf_lines[qid][self.srv_prefix] = json_body[gene_name]
                        except:
                            if self.error_logfile is not None:
                                cur_dt = datetime.datetime.now()
                                date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                                print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc(), file=self.error_logfile+str(date_time)+'.log')
                            else:
                                print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc())
            except:
                print(": error processing variant response: ;", traceback.format_exc())


        return vcf_lines
