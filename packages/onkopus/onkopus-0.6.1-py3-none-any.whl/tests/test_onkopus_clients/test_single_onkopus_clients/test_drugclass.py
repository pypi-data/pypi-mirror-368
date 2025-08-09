import unittest, copy
import onkopus.onkopus_clients

class DrugClassAnnotationTestCase(unittest.TestCase):

    def test_drugclass_client(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}, "chr17:7673776G>A": {}}

        variant_data = onkopus.onkopus_clients.UTAAdapterClient(
            genome_version=genome_version).process_data(data)

        variant_data = onkopus.onkopus_clients.MetaKBClient(
            genome_version=genome_version).process_data(variant_data)

        variant_data = onkopus.onkopus_clients.CIViCClient(
            genome_version=genome_version).process_data(variant_data)

        variant_data = onkopus.onkopus_clients.OncoKBClient(
            genome_version=genome_version).process_data(variant_data)

        variant_data = onkopus.onkopus_clients.AggregatorClient(genome_version).process_data(variant_data)

        variant_data = onkopus.onkopus_clients.DrugOnClient(
            genome_version=genome_version).process_data(variant_data)

        #print("Response ",variant_data)
        for var in variant_data.keys():
            print(variant_data[var]["drug_classes"])
        print(variant_data["chr7:140753336A>T"]["onkopus_aggregator"]["merged_match_types_data"][0]["drugs"])
        self.assertListEqual(variant_data["chr7:140753336A>T"]["onkopus_aggregator"]["merged_match_types_data"][0]["drugs"][1]["drug_class"],['ANTINEOPLASTIC--PI3K Inhibitor'],"")

