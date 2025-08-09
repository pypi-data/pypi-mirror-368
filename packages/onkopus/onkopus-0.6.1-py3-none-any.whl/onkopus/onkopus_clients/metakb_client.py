import datetime, traceback, copy
import adagenes.tools.module_requests as req
import adagenes.tools.parse_vcf
from onkopus.conf import read_config as config
import adagenes.tools


class MetaKBClient:
    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.url_pattern = config.metakb_src
        self.srv_prefix = config.metakb_srv_prefix
        self.extract_keys = config.metakb_keys
        self.info_lines = config.metakb_info_lines
        self.error_logfile = error_logfile

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"

    def process_data(self, vcf_lines, input_format='json'):
        vcf_linesf = adagenes.tools.filter_wildtype_variants(vcf_lines)

        if input_format == 'vcf':
            keys = [config.uta_adapter_srv_prefix + config.concat_char + config.uta_genomic_keys[0],
                    config.uta_adapter_srv_prefix + config.concat_char + config.uta_genomic_keys[1]]
            annotations = adagenes.tools.parse_vcf.extract_annotations_vcf(vcf_linesf, keys)
        else:
            keys = [config.uta_genomic_keys[0],
                    config.uta_genomic_keys[1]]
            annotations = adagenes.tools.parse_vcf.extract_annotations_json(vcf_linesf, config.uta_adapter_srv_prefix, keys)

        gene_names = copy.deepcopy(annotations[keys[0]])
        varexch = copy.deepcopy(annotations[keys[1]])
        qid_list = copy.deepcopy(annotations['q_id'])

        while True:
            max_length = int(config.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            if max_length > len(qid_list):
                max_length = len(qid_list)
            qids_partial = qid_list[0:max_length]
            qids_partial = adagenes.tools.filter_alternate_alleles(qids_partial)

            genompos_str = ','.join(qids_partial)
            gene_names_partial = gene_names[0:max_length]
            variant_exchange_partial = varexch[0:max_length]
            variants_str=''

            for i,query_id in enumerate(qids_partial):
                variants_str += gene_names_partial[i] + ":" + variant_exchange_partial[i] + ","
            variants_str = variants_str.rstrip(",")
            query = 'variants=' + variants_str
            query += '&genompos=' + genompos_str

            try:
                    q = query
                    q += '&size=1000'
                    q += '&key=genompos'

                    json_body = req.get_connection(q, self.url_pattern, self.genome_version)

                    for genompos in json_body.keys():
                            json_obj = json_body[genompos]
                            qid = genompos

                            for k in self.extract_keys:
                                if k in json_obj:
                                    pass
                            try:
                                vcf_lines[qid][self.srv_prefix] = copy.deepcopy(json_obj)
                            except:
                                if self.error_logfile is not None:
                                    cur_dt = datetime.datetime.now()
                                    date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                                    print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc(), file=self.error_logfile+str(date_time)+'.log')
                                else:
                                    print(traceback.format_exc())
            except:
                    if self.error_logfile is not None:
                        print("error processing request: ", q, file=self.error_logfile+str(date_time)+'.log')
                    else:
                        print(": error processing variant response: ;", traceback.format_exc())

            for i in range(0, max_length):
                del gene_names[0]
                del varexch[0]
                del qid_list[0]
            if len(qid_list) == 0:
                break

        return vcf_lines
