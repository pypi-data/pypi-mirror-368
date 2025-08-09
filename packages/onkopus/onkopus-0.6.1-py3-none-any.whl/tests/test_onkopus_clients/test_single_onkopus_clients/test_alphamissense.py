import unittest
import onkopus.onkopus_clients


class AlphaMissenseAnnotationTestCase(unittest.TestCase):

    def test_alphamissense_client(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}, "chr7:140753336A>G": {}}

        variant_data = onkopus.onkopus_clients.AlphaMissenseClient(
            genome_version=genome_version).process_data(data)

        print("Response ",variant_data)


