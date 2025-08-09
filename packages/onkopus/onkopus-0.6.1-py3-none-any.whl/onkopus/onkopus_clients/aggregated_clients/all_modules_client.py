import onkopus
from onkopus.conf import read_config as config


class AllModulesClient:

    def __init__(self, genome_version):
        self.queryid = 'q_id'
        self.genome_version = genome_version
        self.srv_prefix=config.all_modules_srv_prefix
        self.extract_keys = config.all_modules_keys

    def process_data(self, biomarker_data):

        biomarker_data = onkopus.annotate(biomarker_data).data # .annotate_variant_data(biomarker_data)

        return biomarker_data
