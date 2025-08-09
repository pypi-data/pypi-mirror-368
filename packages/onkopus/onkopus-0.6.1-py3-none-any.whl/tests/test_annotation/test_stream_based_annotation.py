import unittest, os
import onkopus as op
import adagenes as ag


class TestCLIAnnotation(unittest.TestCase):

    def test_stream_based_annotation_revel(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        #infile = __location__ + "/../test_files/somaticMutations__cclab_brca.GRCh38.vcf"
        infile = __location__ + "/../test_files/somaticMutations.hg38.ln200.vcf"
        outfile = __location__ + "/../test_files/somaticMutations.hg38.ln200" + ".clinvar.vcf"
        #outfile = __location__ + "/../test_files/somaticMutations__cclab_brca" + ".GRCh38.vcf"

        #client = op.LiftOverClient(genome_version="hg19",target_genome="hg38")
        client = op.ClinVarClient(genome_version="hg38")
        #client = op.DBNSFPClient(genome_version="hg38")
        ag.process_file(infile, outfile, client, genome_version="hg38")

    def test_csv_protein_to_genome_stream(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/tp53_mutations2.csv"
        outfile = __location__ + "/../test_files/tp53_mutations2.vcf"

        mapping = {"gene": "genename", "variant": "variantname"}
        client = op.CCSGeneToGenomicClient(genome_version="hg38")
        ag.process_file(infile,outfile,client,mapping=mapping)
        #self.assertEqual("z","","")



