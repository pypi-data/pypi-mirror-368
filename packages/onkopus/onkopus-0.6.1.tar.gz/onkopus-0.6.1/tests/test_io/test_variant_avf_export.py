import unittest, os
import onkopus as op
import adagenes as ag


class VariantVCFExportTestCase(unittest.TestCase):

    def test_vcf_export_patho(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + '/../test_files/somaticMutations.ln50.avf'
        outfile = __location__ + "/../test_files/somaticMutations.ln50.out.avf"

        bframe = op.read_file(infile, genome_version="hg19")
        bframe = ag.LiftoverClient().process_data(bframe,target_genome="hg38")

        bframe.data = op.DBNSFPClient(genome_version="hg38").process_data(bframe.data)

        op.write_file(outfile, bframe)
