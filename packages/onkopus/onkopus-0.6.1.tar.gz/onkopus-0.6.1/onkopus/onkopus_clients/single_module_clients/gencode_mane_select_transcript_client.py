import datetime, traceback, copy
import adagenes.tools
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config
from adagenes.tools import generate_variant_dictionary


class GENCODEMANESelectClient:
    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.url_pattern = config.gencode_mane_select_transcript_src
        self.srv_prefix = config.gencode_mane_select_transcript_srv_prefix
        self.extract_keys = config.gencode_keys
        self.info_lines = config.gencode_info_lines
        self.error_logfile = error_logfile

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"

    def process_data(self, vcf_lines, input_format='json'):
        if input_format == 'vcf':
            keys = ['POS_hg38']
            annotations = adagenes.tools.parse_vcf.extract_annotations_vcf(vcf_lines, keys)
        else:
            keys = ['POS_hg38']
            annotations = adagenes.tools.parse_vcf.extract_annotations_json(vcf_lines, config.variant_data_key, keys)
        pos_hg38_list = copy.deepcopy(annotations["POS_hg38"])
        print("hg38 positions: ",pos_hg38_list)

        if self.genome_version != "hg38":
            print("Error: GENCODE genomic only possible for hg38 requests")
            return vcf_lines
        qid_list = copy.deepcopy(annotations['q_id'])

        qid_list = list(vcf_lines.keys())

        while True:
            max_length = int(config.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            if max_length > len(qid_list):
                max_length = len(qid_list)
            qids_partial = qid_list[0:max_length]
            qids_partial = adagenes.tools.filter_alternate_alleles(qids_partial)
            genompos_str = ','.join(qids_partial)
            gene_names_partial = \
                adagenes.tools.parse_vcf.extract_annotations_json_part(vcf_lines, config.uta_adapter_srv_prefix,[config.uta_genomic_keys[0]],
                                                                     qids_partial)[config.uta_genomic_keys[0]]
            gene_names_str = ",".join(gene_names_partial)
            query = 'genompos=' + genompos_str
            query = '?' + query + '&response_type=grouped'

            try:
                json_body = req.get_connection(query, self.url_pattern, "hg38")

                for qid in json_body.keys():
                        if qid not in vcf_lines:
                            continue

                        try:
                            qid_orig = qid
                            if len(json_body[qid])>0:
                                vcf_lines[qid_orig][self.srv_prefix] = json_body[qid][0]

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

        return vcf_lines
