import traceback, copy
import adagenes as ag
from onkopus.conf import read_config as config


class LiftOverClient:

    def __init__(self, genome_version, target_genome=None, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines = config.uta_adapter_liftover_info_lines
        self.url_pattern = config.uta_adapter_liftover_src
        self.srv_prefix = config.uta_adapter_liftover_srv_prefix
        self.genomic_keys = config.uta_genomic_keys
        self.gene_keys = config.uta_liftover_gene_keys
        self.gene_response_keys = config.uta_liftover_response_keys
        self.extract_keys = config.uta_liftover_gene_keys
        self.target_genome = target_genome

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"

    def process_data(self, vcf_lines, target_genome="hg38", input_format='json'):
        return ag.LiftoverClient(genome_version=self.genome_version,target_genome=self.target_genome).process_data(vcf_lines, genome_version=self.genome_version, target_genome=target_genome)

