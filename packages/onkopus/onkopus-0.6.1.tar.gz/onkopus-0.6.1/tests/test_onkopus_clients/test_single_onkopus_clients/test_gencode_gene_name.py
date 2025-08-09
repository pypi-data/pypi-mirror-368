import unittest, copy
import onkopus.onkopus_clients


class GencodeGeneNameTestCase(unittest.TestCase):

    def test_gencode_client(self):
        genome_version = 'hg19'

        data = {"TP53": {}, "KRAS": {}}

        #variant_data = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version).process_data(data)
        variant_data = onkopus.onkopus_clients.GENCODEGeneNameClient(
            genome_version=genome_version).process_data(data)

        print("Response ",variant_data)

