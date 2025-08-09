import unittest, os
import onkopus.onkopus_clients

class COSMICAnnotationTestCase(unittest.TestCase):

    def test_cosmic_client_snv(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}}

        variant_data = onkopus.UTAAdapterClient(genome_version=genome_version).process_data(data)
        variant_data = onkopus.onkopus_clients.COSMICGeneCensusClient(
            genome_version=genome_version).process_data(variant_data)

        print("Response ",variant_data)

    def test_cosmic_client_gene(self):
        genome_version = 'hg38'

        data = {"BRAF": {}}

        variant_data = onkopus.onkopus_clients.COSMICGeneCensusClient(
            genome_version=genome_version).process_data(data,gene_request=True)

        print("Response ",variant_data)
