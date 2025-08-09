import unittest, os
import onkopus as op
import adagenes as ag


class TestCLIAnnotation(unittest.TestCase):

    def test_stream_based_annotation_revel(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        #infile = __location__ + "/../test_files/somaticMutations__cclab_brca.GRCh38.vcf"
        infile = __location__ + "/../test_files/somaticMutations" + ".vcf"
        outfile = __location__ + "/../test_files/somaticMutations" + ".ann.vcf"
        #outfile = __location__ + "/../test_files/somaticMutations__cclab_brca" + ".GRCh38.vcf"

        #client = op.LiftOverClient(genome_version="hg19",target_genome="hg38")
        #client = op.ClinVarClient(genome_version="hg38")
        client = op.AllModulesClient(genome_version="hg19")
        ag.process_file(infile, outfile, client, genome_version="hg19")

