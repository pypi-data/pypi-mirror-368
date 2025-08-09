import datetime, traceback, copy
import adagenes.tools
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config
from adagenes.tools import generate_variant_dictionary
import onkopus as op

def collect_affected_genes(json_body):

    genes_str = ''
    cds_str = ''
    utr_str = ''

    if isinstance(json_body,dict):
        if "gene" in json_body:
            for gene in json_body["gene"]:
                #print("affetced gene ",gene)
                if " gene_name" in gene:
                    gene_name = gene[" gene_name"]
                    genes_str += gene_name + "_"
        if "cds" in json_body:
            for cds in json_body["cds"]:
                cstr = cds[" gene_name"] + "_" + str(cds[" seqname"]) + ":" + str(cds[" start_pos"]) + "-" + str(cds[" end_pos"]) + "(" + str(cds[" strand"]) + ")"
                cds_str += cstr + '_'
        if "utr" in json_body:
            for utr in json_body["utr"]:
                ustr = utr[" gene_name"] + "_" + str(utr[" seqname"]) + ":" + str(utr[" start_pos"]) + "-" + str(utr[" end_pos"]) + "(" + str(utr[" strand"]) + ")"
                utr_str += ustr + "_"
    genes_str = genes_str.rstrip("_")
    cds_str = cds_str.rstrip("_")
    utr_str = utr_str.rstrip("_")

    json_body["Affected_genes"] = genes_str
    json_body["Affected_CDS"] = cds_str
    json_body["Affected_UTRs"] = utr_str

    return json_body


def get_qid_list(vcf_lines):

    qid_dc = {}
    qid_list = []

    for var in vcf_lines.keys():
        if "variant_data" in vcf_lines[var]:
            if "POS2" in vcf_lines[var]["variant_data"]:
                chrom = str(vcf_lines[var]["variant_data"]["CHROM"])
                pos = str(vcf_lines[var]["variant_data"]["POS"])
                pos2 = str(vcf_lines[var]["variant_data"]["POS2"])
            else:
                continue
        elif "chrom" in vcf_lines[var]:
            if "pos2" in vcf_lines[var]:
                chrom = str(vcf_lines[var]["chrom"])
                pos = str(vcf_lines[var]["pos"])
                pos2 = str(vcf_lines[var]["pos2"])
            else:
                continue
        elif "CHROM" in vcf_lines[var]:
            if "POS2" in vcf_lines[var]:
                chrom = str(vcf_lines[var]["CHROM"])
                pos = str(vcf_lines[var]["POS"])
                pos2 = str(vcf_lines[var]["POS2"])
            else:
                continue
        else:
            continue
        if "chr" not in chrom:
            chrom = "chr" + chrom
        qid = chrom + ":" + pos + "-" + pos2
        qid_list.append(qid)

        qid_dc[qid] = var

    return qid_dc, qid_list


class CNVGeneClient:
    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.url_pattern = config.cnv_genomic_src
        self.srv_prefix = config.cnv_genomic_srv_prefix
        self.extract_keys = config.cnv_keys
        self.info_lines = config.cnv_info_lines
        self.error_logfile = error_logfile

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"

    def process_data(self, vcf_lines, input_format='json'):

        #print("Annotate CNAs ",vcf_lines)

        mut_types = False
        if (len(list(vcf_lines.keys())) == 5) and ("snvs" in list(vcf_lines.keys())):
            vcf_lines_cp = copy.deepcopy(vcf_lines)
            vcf_lines = vcf_lines["snvs"]
            mut_types = True

        if input_format == 'vcf':
            keys = ['POS_hg38']
            annotations = adagenes.tools.parse_vcf.extract_annotations_vcf(vcf_lines, keys)
        else:
            keys = ['POS_hg38']
            annotations = adagenes.tools.parse_vcf.extract_annotations_json(vcf_lines, config.variant_data_key, keys)
        pos_hg38_list = copy.deepcopy(annotations["POS_hg38"])
        #print("hg38 positions: ",pos_hg38_list)

        if self.genome_version != "hg38":
            print("Error: GENCODE genomic only possible for hg38 requests")
            return vcf_lines
        qid_list = copy.deepcopy(annotations['q_id'])
        #qid_list = copy.deepcopy(list(vcf_lines.keys()))

        #variant_dc, liftover_dc = adagenes.tools.parse_genomic_data.generate_liftover_qid_list(qid_list, pos_hg38_list)

        #qid_list = list(vcf_lines.keys())
        #qid_list = list(liftover_dc.keys())
        qid_dc, qid_list = get_qid_list(vcf_lines)

        while True:
            max_length = int(config.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            if max_length > len(qid_list):
                max_length = len(qid_list)
            qids_partial = qid_list[0:max_length]
            qids_partial = adagenes.tools.filter_alternate_alleles(qids_partial)
            genompos_str = ','.join(qids_partial)
            # adagenes.tools.parse_vcf.extract_annotations_json_part(vcf_lines, config.uta_adapter_srv_prefix,[config.uta_genomic_keys[0]],
            #                                                     qids_partial)[config.uta_genomic_keys[0]]
            #gene_names_partial =  op.get_gene_names(vcf_lines)
            #gene_names_str = ",".join(gene_names_partial)
            query = 'genompos=' + genompos_str
            query = '?' + query + '&response_type=grouped'

            try:
                json_body = req.get_connection(query, self.url_pattern, "hg38")

                for qid in json_body.keys():
                        #annotations = []

                        if qid not in qid_dc.keys():
                        #if qid not in vcf_lines:
                            continue
                        #qid = json_obj[self.qid_key]

                        try:
                            json_body[qid] = collect_affected_genes(json_body[qid])
                            #if self.genome_version == "hg19":
                            #    qid_orig = liftover_dc[qid]
                            #else:
                            #    qid_orig = qid
                            #qid_orig = qid
                            qid_orig = qid_dc[qid]
                            #print("assign ",qid_orig)
                            vcf_lines[qid_orig][self.srv_prefix] = json_body[qid]

                            #if len(json_body[qid]["gene"]) > 0:
                            #    if "gene" not in vcf_lines[qid_orig]["variant_data"]:
                            #        #print(json_body[qid]["gene"][0])
                            #        vcf_lines[qid_orig]["variant_data"]["gene"] = json_body[qid]["gene"][0][" gene_name"]
                        except:
                            if self.error_logfile is not None:
                                cur_dt = datetime.datetime.now()
                                date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                                print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc(), file=self.error_logfile+str(date_time)+'.log')
                            else:
                                print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc())
            except:
                print(": error processing variant response: ;", traceback.format_exc())
                if self.error_logfile is not None:
                    print("error processing request: ", annotations, file=self.error_logfile+str(date_time)+'.log')

            for i in range(0,max_length):
                #del gene_names[0] #gene_names.remove(qid)
                #del variant_exchange[0]  #variant_exchange.remove(qid)
                del qid_list[0] # qid_list.remove(qid)
            if len(qid_list) == 0:
                break

        if mut_types is True:
            vcf_lines_cp["snvs"] = vcf_lines
            return vcf_lines_cp

        return vcf_lines
