import unittest, copy
import onkopus.onkopus_clients

class VUSPredictAnnotationTestCase(unittest.TestCase):

    def test_vus_predict_client(self):
        genome_version = 'hg19'

        data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}}

        data = onkopus.onkopus_clients.UTAAdapterClient(
            genome_version=genome_version).process_data(data)

        variant_data = onkopus.onkopus_clients.VUSPredictClient(
            genome_version=genome_version).process_data(data)

        print("Response ",variant_data)


