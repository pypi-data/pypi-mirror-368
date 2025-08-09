from adagenes.tools import get_biomarker_type_aaexchange


class BiomarkerRecognitionClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version

    def process_data(self,annotated_data):

        annotated_data = get_biomarker_type_aaexchange(annotated_data)

        return annotated_data
