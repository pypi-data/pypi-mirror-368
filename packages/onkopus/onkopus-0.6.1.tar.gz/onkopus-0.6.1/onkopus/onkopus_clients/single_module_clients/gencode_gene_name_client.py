import datetime, traceback, copy
import adagenes.tools
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config


class GENCODEGeneNameClient:
    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.url_pattern = config.gencode_src
        self.srv_prefix = config.gencode_srv_prefix
        self.extract_keys = config.gencode_keys
        self.info_lines = config.gencode_info_lines
        self.error_logfile = error_logfile

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"

    def process_data(self, vcf_lines, input_format='json'):

        if input_format == 'vcf':
            keys = [config.uta_adapter_srv_prefix + config.concat_char + config.uta_genomic_keys[0]]
            annotations = adagenes.tools.parse_vcf.extract_annotations_vcf(vcf_lines, keys)
        else:
            keys = [config.uta_genomic_keys[0]]
            annotations = adagenes.tools.parse_vcf.extract_annotations_json(vcf_lines, config.uta_adapter_srv_prefix, keys)

        qid_list = list(vcf_lines.keys())

        while True:
            max_length = int(config.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            if max_length > len(qid_list):
                max_length = len(qid_list)
            qids_partial = qid_list[0:max_length]
            qids_partial = adagenes.tools.filter_alternate_alleles(qids_partial)
            genompos_str = ','.join(qids_partial)
            gene_names_partial = list(vcf_lines.keys())
            gene_names_str = ",".join(gene_names_partial)
            query = 'genes=' + gene_names_str
            query = '?' + query + '&response_type=grouped'
            #dc = adagenes.tools.parse_genomic_data.generate_dictionary(gene_names_partial,qids_partial)

            try:
                json_body = req.get_connection(query, self.url_pattern, "hg38")

                for gene_name in json_body.keys():

                        qid = gene_name#dc[gene_name]

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
                if self.error_logfile is not None:
                    print("error processing request: ", annotations, file=self.error_logfile+str(date_time)+'.log')

            for i in range(0,max_length):
                del qid_list[0]
            if len(qid_list) == 0:
                break

        return vcf_lines
