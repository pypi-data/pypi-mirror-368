import unittest
import onkopus as op


class TestAnnotationMultipleTypes(unittest.TestCase):

    def test_gene_annotation(self):
        data = {
            "TP53":{ "mutation_type": "gene" },
            "chr7:140753336A>T": { }
        }
        data = op.annotate_genes(data)
        print(data)

