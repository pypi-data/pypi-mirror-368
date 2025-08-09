import unittest
import onkopus.onkopus_clients
import adagenes as ag


class UTAAdapterProteinSequenceAnnotationTestCase(unittest.TestCase):

    def test_pseq_client_hg19(self):
        genome_version = 'hg19'
        data = {"chr7:140453136A>T": {}}
        variant_data = ag.LiftoverAnnotationClient(genome_version=genome_version,target_genome="hg38").process_data(data)
        print("lift over ",variant_data)
        variant_data = onkopus.onkopus_clients.UTAAdapterClient(
            genome_version=genome_version).process_data(variant_data)
        variant_data = onkopus.onkopus_clients.UTAAdapterProteinSequenceClient(
            genome_version=genome_version).process_data(variant_data)
        print("Response ", variant_data)
        self.assertEqual(variant_data["chr7:140453136A>T"]["UTA_Adapter_protein_sequence"]["protein_sequence"][:18],
                         "MAALSGGGGGGAEPGQAL", "")

    def test_uta_adapter_protein_sequence_client_variant(self):
        genome_version = 'hg38'
        data = {"chr7:140753336A>T": {}, "chr10:8115913C>T":{},"chr7:140753336A>G": {}}
        variant_data = onkopus.onkopus_clients.UTAAdapterClient(
            genome_version=genome_version).process_data(data)
        variant_data = onkopus.onkopus_clients.UTAAdapterProteinSequenceClient(
            genome_version=genome_version).process_data(variant_data)
        print("Response ",variant_data)
        self.assertEqual(variant_data["chr7:140753336A>T"]["UTA_Adapter_protein_sequence"]["protein_sequence"][:18],"MAALSGGGGGGAEPGQAL","")

    def test_uta_adapter_protein_sequence_client_gene(self):
        genome_version = 'hg38'
        data = {"BRAF": {}, "NRAS": {}}
        variant_data = onkopus.onkopus_clients.UTAAdapterProteinSequenceClient(
            genome_version=genome_version).process_data(data,gene_request=True)
        print("Response ",variant_data)
        self.assertListEqual(list(variant_data.keys()),["BRAF","NRAS"],"")

