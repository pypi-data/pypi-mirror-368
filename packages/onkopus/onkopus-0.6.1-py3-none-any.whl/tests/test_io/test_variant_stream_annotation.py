import unittest, os
import onkopus as op
import adagenes as ag

class TestStreamAnnotation(unittest.TestCase):

    def test_stream_vcf_liftover(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + '/../test_files/somaticMutations.ln50.vcf'
        outfile = __location__ + "/../test_files/somaticMutations.hg38.ln50.lo.vcf"

        client = op.LiftOverClient(genome_version="hg19", target_genome="hg38")
        ag.process_file(infile,outfile,client)

        with open(outfile, 'r') as file:
            contents = file.read()

        cont_expected = ('Adapter-LiftOver,Number=1,Type=String,Description="Reference Genome '
 'LiftOver">\n'
 '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n'
 'chr7\t21744593\t.\tA\tAG\t.\t.\t.\n'
 'chr10')

        self.assertEqual(contents[50:200], cont_expected, "")

    def test_stream_vcf_annotate_clinvar(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + '/../test_files/somaticMutations.hg38.ln50.vcf'
        outfile = __location__ + "/../test_files/somaticMutations.hg38.ln50.clinvar.out.vcf"

        client = op.ClinVarClient(genome_version="hg38")
        ag.process_file(infile,outfile,client,genome_version="hg38")

        #with open(outfile, 'r') as file:
        #    contents = file.read()

        #self.assertEqual(contents[50:400],
        #                 'Adapter-LiftOver,Number=1,Type=String,Description="Reference Genome '
        #                 'LiftOver">\n'
        #                 'chr#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO;\n'
        #                 'chr7\t21744592\t.\tA\tAG\t.\t.\t.\n'
        #                 'chr10\t8073950\t.\tC\tT\t.\t.\t.\n'
        #                 'chr17\t7778426\t.\tT\tC\t.\t.\t.\n'
        #                 'chr1\t148998357\t.\tG\tA\t.\t.\t.\n'
        #                 'chr1\t237638364\t.\tG\tA\t.\t.\t.\n'
        #                 'chr5\t13882966\t.\tC\tT\t.\t.\t.\n'
        #                 'chr7\t92029936\t.\tA\tG\t.\t.\t.\n'
        #                 'chr11\t62520346\t.\tC\tT\t.\t.\t.\n'
        #                 'chr11\t62524581\t.'
        #                 , "")
