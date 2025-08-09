import unittest, copy
import onkopus as op


class DGIDBAnnotationTestCase(unittest.TestCase):

    def test_dgidb_gene_request(self):
        genome_version="hg38"
        data = {"BRAF":{}}
        data = op.DGIdbClient(genome_version=genome_version).process_data(data, gene_request=True)
        self.assertEqual(data["BRAF"]["dgidb"]["summary"][:20], "SORAFENIB:inhibitor:", "")

    def test_dgidb_client(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}, "chr1:2556710C>A": {},
                "chr1:2556710C>T":{},"chr1:2556714A>G":{}, "chr1:2556718C>T":{}}

        variant_data = op.UTAAdapterClient(
            genome_version=genome_version).process_data(data)
        variant_data = op.DGIdbClient(genome_version=genome_version).process_data(variant_data)

        print("Response ",variant_data["chr7:140753336A>T"]["dgidb"]["summary"])
        self.assertEqual(variant_data["chr7:140753336A>T"]["dgidb"]["summary"][:20],"SORAFENIB:inhibitor:","")
