import unittest
import onkopus as op
import adagenes as ag


class TestGeneAnnotation(unittest.TestCase):

    def test_gene_annotation(self):
        data = {"TP53":{ "mutation_type": "gene" }}
        bframe = ag.BiomarkerFrame(data)
        data = op.annotate_genes(bframe.data)
        print(data["TP53"].keys())
        #print(data)
        self.assertEqual(set(list(data["TP53"].keys())),
                         set(['mutation_type', 'type', 'mdesc', 'cosmic', 'civic', 'dgidb', 'gencode', 'onkopus_aggregator', 'UTA_Adapter']),
                         "")

