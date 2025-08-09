import datetime, requests, traceback, copy
import adagenes as ag
from onkopus.conf import read_config as config
import adagenes.tools

qid_key = "q_id"
error_logfile=None


class REVELClient:
    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines = config.revel_info_lines
        self.url_pattern = config.revel_src
        self.srv_prefix = config.revel_srv_prefix
        self.extract_keys = config.revel_keys

        self.qid_key = "target"
        #if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
        #    self.qid_key = "q_id_hg19"

    def process_data(self, vcf_lines):

        vcf_linesf = adagenes.tools.filter_wildtype_variants(vcf_lines)

        qid_dc = {}
        if self.genome_version == "hg38":
            qid_list = copy.deepcopy(list(vcf_linesf.keys()))
        else:
            qid_dc, qid_list = ag.tools.generate_qid_list_from_other_reference_genome(vcf_linesf)
            self.genome_version = "hg38"
            retransform = True
        #qid_dc, qid_list = ag.tools.generate_qid_list_from_other_reference_genome(vcf_linesf)
        self.genome_version = "hg38"

        while True:
            max_length = int(config.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            if max_length > len(qid_list):
                max_length = len(qid_list)
            qids_partial = qid_list[0:max_length]

            q = ','.join(adagenes.tools.filter_alternate_alleles(qids_partial))

            vcf_lines = adagenes.processing.parse_http_responses.parse_module_response(q, vcf_lines, self.url_pattern,
                                                                                     self.genome_version,
                                                                                     self.srv_prefix,
                                                                                       qid_dc)

            for i in range(0, max_length):
                del qid_list[0]
            if len(qid_list) == 0:
                break

        return vcf_lines
