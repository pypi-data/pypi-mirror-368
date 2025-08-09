import traceback, datetime, json
import onkopus as op
from onkopus.conf import read_config as config


class PathogenicityClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines= config.onkopus_aggregator_info_lines
        self.url_pattern = config.onkopus_aggregator_src
        self.srv_prefix = config.onkopus_aggregator_srv_prefix
        self.response_keys = config.onkopus_aggregator_response_keys
        self.extract_keys = config.onkopus_aggregator_keys

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"
        self.error_logfile = error_logfile

    def process_data(self, biomarker_data):

        # dbNSFP
        biomarker_data = op.DBNSFPClient(self.genome_version).process_data(biomarker_data)

        # REVEL
        biomarker_data = op.REVELClient(self.genome_version).process_data(biomarker_data)

        # AlphaMissense
        biomarker_data = op.AlphaMissenseClient(self.genome_version).process_data(biomarker_data)

        # LoFTool
        biomarker_data = op.LoFToolClient(self.genome_version).process_data(biomarker_data)

        return biomarker_data
