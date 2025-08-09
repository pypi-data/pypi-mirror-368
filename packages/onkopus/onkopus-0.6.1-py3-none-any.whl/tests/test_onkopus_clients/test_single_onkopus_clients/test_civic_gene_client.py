import unittest
import onkopus.onkopus_clients


class CIViCGeneTestCase(unittest.TestCase):

    def test_civic_client(self):
        genome_version = 'hg19'

        data = {"KRAS": {}, "TP53": {}}

        variant_data = onkopus.onkopus_clients.CIViCGeneClient(
            genome_version=genome_version).process_data(data)

        print("Response ",variant_data)
