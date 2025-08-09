import unittest
import onkopus as op


class TestGeneFusionClient(unittest.TestCase):

    def test_gene_fusion_client(self):
        genome_version = 'hg38'
        data = {"chr7:47344754-chr7:55157662": {}}
        variant_data = op.CCSGeneFusionClient(
            genome_version=genome_version).process_data(data)
        print("Response ", variant_data)

