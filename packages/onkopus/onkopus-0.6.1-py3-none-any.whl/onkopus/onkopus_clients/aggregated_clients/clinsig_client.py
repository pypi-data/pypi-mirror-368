import traceback, datetime, json
import onkopus as op
from onkopus.conf import read_config as config


class ClinSigClient:

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

        biomarker_data = op.UTAAdapterClient(self.genome_version).process_data(biomarker_data)

        # OncoKB
        biomarker_data = op.OncoKBClient(self.genome_version).process_data(biomarker_data)

        # CIViC
        biomarker_data = op.CIViCClient(self.genome_version).process_data(biomarker_data)

        # MetaKB
        biomarker_data = op.MetaKBClient(self.genome_version).process_data(biomarker_data)

        # Aggregate evidence data
        biomarker_data = op.AggregatorClient(self.genome_version).process_data(biomarker_data)

        return biomarker_data
