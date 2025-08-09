import unittest, copy
import onkopus.onkopus_clients


class DrugClassedTestCase(unittest.TestCase):

    def test_get_drug_list(self):
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
        variant_data = onkopus.onkopus_clients.AggregatorClient(
            genome_version=genome_version).process_data(variant_data)

        drug_list = onkopus.onkopus_clients.DrugOnClient(genome_version).get_drug_list(list(variant_data.keys()),variant_data)
        print(drug_list)

    def test_get_drug_classes(self):
        genome_version = 'hg38'

        drug_list = ["Vemurafenib", "Cetuximab", "Olaparib"]

        drug_classifications = onkopus.onkopus_clients.DrugOnClient(genome_version).get_drug_classes(drug_list)
        print("Response ", drug_classifications)

