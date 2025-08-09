import unittest
import onkopus.onkopus_clients

class MetaKBAnnotationTestCase(unittest.TestCase):

    def test_metakb_client(self):

        genome_version = 'hg38'
        qid = "chr7:140753336A>T"
        data = {qid: {}}
        data = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version).process_data(data)
        variant_data = onkopus.onkopus_clients.MetaKBClient(
            genome_version=genome_version).process_data(data)

        self.assertEqual(len(variant_data[qid]["metakb"]["metakb_features_norm"]["exact_match"]), 573,
                         "Error retrieving MetaKB response")

