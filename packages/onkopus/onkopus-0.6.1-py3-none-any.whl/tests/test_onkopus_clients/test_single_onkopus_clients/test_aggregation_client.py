import unittest
import onkopus


class AggregationTestCase(unittest.TestCase):

    def test_aggregator_client(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}, "chr12:25245350C>T": {}}

        variant_data = onkopus.onkopus_clients.uta_adapter_client.UTAAdapterClient(
            genome_version=genome_version).process_data(data)
        print("uta response", variant_data)

        client = onkopus.onkopus_clients.MetaKBClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        client = onkopus.onkopus_clients.CIViCClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        client = onkopus.onkopus_clients.OncoKBClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)

        # Aggregator
        variant_data = onkopus.onkopus_clients.aggregator_client.AggregatorClient(
            genome_version=genome_version).process_data(variant_data)

        #print("Aggregator response ",variant_data)
        self.assertEqual(len(variant_data["chr7:140753336A>T"]["onkopus_aggregator"]["merged_match_types_data"]), 701, "")
        self.assertListEqual(list(variant_data["chr7:140753336A>T"].keys()),
                             ['variant_data', 'UTA_Adapter', 'metakb', 'civic', 'onkopus_aggregator'], "")
