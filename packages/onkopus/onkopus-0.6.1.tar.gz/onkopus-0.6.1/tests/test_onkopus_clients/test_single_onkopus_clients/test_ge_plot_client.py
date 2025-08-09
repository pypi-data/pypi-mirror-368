import unittest
import onkopus as op


class GEPlotTestCase(unittest.TestCase):

    def test_ge_plot_client(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}, "chr12:25245350C>T": {}}

        variant_data = op.uta_adapter_client.UTAAdapterClient(
            genome_version=genome_version).process_data(data)
        print("uta response", variant_data)

        variant_data = op.GeneExpressionPlotClient().process_data(variant_data["chr7:140753336A>T"])
        print(variant_data)

        self.assertEqual(variant_data['BRAF']['data'][0]['marker']['color'], "lightskyblue", "")

