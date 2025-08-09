import datetime, traceback, copy
import adagenes.tools.parse_vcf
import adagenes.processing.parse_http_responses
from onkopus.conf import read_config as config
import adagenes.tools.module_requests as req
import onkopus as op

qid_key = "q_id"
error_logfile=None


class COSMICGeneCensusClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines = config.cosmic_info_lines
        self.url_pattern = config.cosmic_src
        self.srv_prefix = config.cosmic_srv_prefix
        self.extract_keys = config.cosmic_keys

        self.qid_key = "q_id"
        self.error_logfile = error_logfile
        #if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
        #    self.qid_key = "q_id_hg19"

    def process_data(self, vcf_lines,gene_request=False):

        # get gene names and variant exchange from passed JSON object
        #if input_format == 'vcf':
        #    keys = [config.uta_adapter_srv_prefix + config.concat_char + config.uta_genomic_keys[0],
        #            config.uta_adapter_srv_prefix + config.concat_char + config.uta_genomic_keys[1]]
        #    annotations = adagenes.tools.parse_vcf.extract_annotations_vcf(vcf_lines, keys)
        #else:
        if gene_request is False:
            keys = [config.uta_genomic_keys[0], config.uta_genomic_keys[1]]
        else:
            keys = list(vcf_lines.keys())
        #annotations = adagenes.tools.parse_vcf.extract_annotations_json(vcf_lines, config.uta_adapter_srv_prefix, keys)

        #gene_names = copy.deepcopy(annotations[keys[0]])
        #varexch = copy.deepcopy(annotations[keys[1]])
        #qid_list = copy.deepcopy(annotations['q_id'])

        qid_gene_name_dc = {}
        qid_list = []
        for qid in vcf_lines.keys():
            variant_data = vcf_lines[qid]
            if ("UTA_Adapter" in variant_data) and (gene_request is False):
                if ("gene_name" in variant_data["UTA_Adapter"]) and (
                        "variant_exchange" in variant_data["UTA_Adapter"]):
                    qid_gene_name_dc[variant_data["UTA_Adapter"]["gene_name"]] = qid
                    qid_list.append(variant_data["UTA_Adapter"]["gene_name"])
            elif gene_request is False:
                print("ProteinFeatures: Could not find UTA adapter section: ", variant_data)
            else:
                qid_list.append(qid)
        q_lists = list(op.tools.divide_list(copy.deepcopy(qid_list), chunk_size=100))

        for q_list in q_lists:
            q = ",".join(q_list)

            #while True:
            max_length = int(config.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            if max_length > len(qid_list):
                max_length = len(qid_list)
            #qids_partial = qid_list[0:max_length]

            #qids_partial = adagenes.tools.filter_alternate_alleles(qids_partial)

            #genompos_str = ','.join(qids_partial)
            #gene_names_partial = \
            #    adagenes.tools.parse_vcf.extract_annotations_json_part(vcf_lines, config.uta_adapter_srv_prefix,
            #                                                         [config.uta_genomic_keys[0]],
            #                                                         qids_partial)[config.uta_genomic_keys[0]]
            #variant_exchange_partial = adagenes.tools.parse_vcf.extract_annotations_json_part(vcf_lines,
            #                                                                                config.uta_adapter_srv_prefix, [
            #                                                                                    config.uta_genomic_keys[
            #                                                                                        1]],
            #                                                                                qids_partial)[
            #    config.uta_genomic_keys[1]]

            #gene_names_str = ",".join(gene_names_partial)
            #variant_exchange_str = ",".join(variant_exchange_partial)

            qid_gene_dc = {}
            q = "?gene=" + q
            #for i in range(0, len(gene_names_partial)):
            #    q += str(gene_names_partial[i]) + ","
            #    qid_gene_dc[gene_names_partial[i]] = qids_partial[i]

            q = q.rstrip(",")
            #q += '&gene=' + genompos_str




            #vcf_lines = adagenes.processing.parse_http_responses.parse_module_response(q, vcf_lines,self.url_pattern,self.genome_version,self.srv_prefix)
            try:
                json_body = req.get_connection(q, self.url_pattern, self.genome_version)

                for key in json_body["cosmic"].keys():
                    json_obj = json_body["cosmic"][key]
                    gene = key

                    try:
                        if gene_request is False:
                            qid = qid_gene_name_dc[gene]
                        else:
                            qid = gene
                        vcf_lines[qid][self.srv_prefix] = json_obj
                    except:
                        cur_dt = datetime.datetime.now()
                        print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc())
            except:
                print(": error processing variant response: ;", traceback.format_exc())

            #for i in range(0, max_length):
            #    del gene_names[0]
            #    del varexch[0]
            #    del qid_list[0]
            #if len(qid_list) == 0:
            #    break

        return vcf_lines
