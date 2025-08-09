import unittest, os
import adagenes
import onkopus as op


class TestProteinToGenomic(unittest.TestCase):

    def test_protein_to_genomic(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/tp53_mutations.csv"
        bframe = adagenes.read_file(infile, genome_version="hg38")

        print("read ",bframe.data)
        bframe = op.ProteinToGenomic().process_data(bframe)

        print(bframe.data.keys())
        qids = ['chr17:7676591C>T', 'chr17:7676591C>G', 'chr17:7676590T>G', 'chr17:7676590T>C', 'chr17:7676589C>A', 'chr17:7676588C>T', 'chr17:7676588C>G', 'chr17:7676587T>G', 'chr17:7676587T>C', 'chr17:7676587T>A', 'chr17:7676586C>A', 'chr17:7676585G>T']
        self.assertListEqual(list(bframe.data.keys()),qids,"Error protein to genomic")

