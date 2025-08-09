import datetime, requests, traceback, copy
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config
import adagenes.tools
from onkopus.onkopus_clients.processing.parse_json import parse_score_results

qid_key = "q_id"
error_logfile=None


class PrimateAIClient:
    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines = config.primateai_info_lines
        self.url_pattern = config.primateai_src
        self.srv_prefix = config.primateai_srv_prefix
        self.extract_keys = config.primateai_keys

        self.qid_key = "q_id"
        self.error_logfile = error_logfile

    def process_data(self, vcf_lines):
        qid_list = copy.deepcopy(list(vcf_lines.keys()))
        while True:
            max_length = int(config.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            if max_length > len(qid_list):
                max_length = len(qid_list)
            qids_partial = qid_list[0:max_length]
            variants = ','.join(adagenes.tools.filter_alternate_alleles(qids_partial))

            try:
                json_body = req.get_connection(variants, self.url_pattern, self.genome_version)
                vcf_lines = parse_score_results(vcf_lines, json_body, self.srv_prefix)
            except:
                if error_logfile is not None:
                    cur_dt = datetime.datetime.now()
                    date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                    print("error processing request: ", variants, file=error_logfile+str(date_time)+'.log')

            for i in range(0, max_length):
                del qid_list[0] 
            if len(qid_list) == 0:
                break

        return vcf_lines
