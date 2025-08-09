import unittest, copy
import onkopus.onkopus_clients

class GencodeMANESelectTestCase(unittest.TestCase):

    def test_gencode_client(self):
        genome_version = 'hg38'
        data = {"chr7:140753336A>T": {}, "chr10:8115913C>T": {}}

        variant_data = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version).process_data(data)
        variant_data = onkopus.onkopus_clients.LiftOverClient(genome_version=genome_version).process_data(variant_data)
        variant_data = onkopus.onkopus_clients.GENCODEMANESelectClient(
            genome_version=genome_version).process_data(variant_data)

        print("Response ",variant_data)


