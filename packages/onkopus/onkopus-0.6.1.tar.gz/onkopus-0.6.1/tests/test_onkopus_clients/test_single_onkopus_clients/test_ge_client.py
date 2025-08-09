import unittest
import adagenes as ag
import onkopus as op


class GETestCase(unittest.TestCase):

    def test_ge_client(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}, "chr12:25245350C>T": {}, "BRAF":{}}
        bframe = ag.BiomarkerFrame(data)
        print("gen bframe ",bframe)

        variant_data = op.uta_adapter_client.UTAAdapterClient(
            genome_version=genome_version).process_data(bframe.data)
        print("uta response", variant_data)

        variant_data = op.GeneExpressionClient().process_data(bframe.data)
        print(variant_data["chr7:140753336A>T"]["gtex"])
        self.assertEqual(variant_data["chr7:140753336A>T"]["gtex"]['Adipose_Subcutaneous'], 7.77011, "")

