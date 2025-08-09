import unittest, copy
import onkopus.onkopus_clients

class GencodeAnnotationTestCase(unittest.TestCase):

    def test_gencode_client(self):
        #genome_version = 'hg19'
        genome_version = 'hg38'

        #data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}}
        data = {"chr7:140753336A>T":{}}

        variant_data = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version).process_data(data)
        variant_data = onkopus.onkopus_clients.GENCODEClient(
            genome_version=genome_version).process_data(variant_data)

        print("Response ",variant_data)

