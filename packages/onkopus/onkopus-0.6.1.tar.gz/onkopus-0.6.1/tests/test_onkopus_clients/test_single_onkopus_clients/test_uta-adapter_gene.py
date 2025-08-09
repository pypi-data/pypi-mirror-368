import unittest
import adagenes as ag
import onkopus.onkopus_clients


class UTAAdapterGeneAnnotationTestCase(unittest.TestCase):

    def test_uta_adapter_genetogenomic_client(self):
        genome_version = 'hg38'
        data = {"NRAS:Q61L": {}, "TP53:R282W": {}}
        bframe = ag.BiomarkerFrame(data)
        print(bframe.data)
        variant_data = onkopus.onkopus_clients.CCSGeneToGenomicClient(
            genome_version=genome_version).process_data(bframe.data)
        variant_data = onkopus.onkopus_clients.UTAAdapterClient(
            genome_version=genome_version).process_data(variant_data)
        variant_data = onkopus.onkopus_clients.CCSGeneToGenomicClient(
            genome_version=genome_version).process_data(variant_data)
        print("Response ",variant_data["chr1:114713908T>A"]["UTA_Adapter"])
        qids = ["chr1:114713908T>A", "chr17:7673776G>A"]
        self.assertListEqual(list(variant_data.keys()), qids, "Error UTA adapter GeneToGenomic")
        self.assertEqual(variant_data["chr1:114713908T>A"]["mutation_type"],"snv","")

    def test_uta_adapter_genetogenomic_geneannotation(self):
        genome_version = 'hg38'
        data = {"chr18:7888143G>A": {}, "chr10:87864472G>A": {}}
        bframe = ag.BiomarkerFrame(data)
        print(bframe.data)
        variant_data = onkopus.onkopus_clients.CCSGeneToGenomicClient(
            genome_version=genome_version).process_data(bframe.data)
        variant_data = onkopus.onkopus_clients.UTAAdapterClient(
            genome_version=genome_version).process_data(variant_data)
        variant_data = onkopus.onkopus_clients.CCSGeneToGenomicClient(
            genome_version=genome_version, data_type="g").process_data(variant_data)
        qids = ["chr18:7888143G>A", "chr10:87864472G>A"]
        self.assertListEqual(list(variant_data.keys()), qids, "Error UTA adapter GeneToGenomic")
        self.assertEqual(variant_data["chr18:7888143G>A"]["UTA_Adapter"]["variant_exchange"], "E78=", "")
