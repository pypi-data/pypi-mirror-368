import unittest, os
import onkopus as op
import adagenes

class TestCustomVCFAnnotation(unittest.TestCase):

    def test_custom_vcf_annotation(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../../test_files/somaticMutations.ln50.vcf"
        genome_version="hg19"
        outfile = infile + ".anno.csv"
        bframe = op.read_file(infile)
        bframe.data = adagenes.LiftoverClient(genome_version="hg19").process_data(bframe.data)
        print(bframe.data)
        bframe.data = op.UTAAdapterClient(bframe.genome_version).process_data(bframe.data)
        bframe.data = op.DBNSFPClient(bframe.genome_version).process_data(bframe.data)
        print(bframe.data)
        op.write_file(outfile, bframe)


