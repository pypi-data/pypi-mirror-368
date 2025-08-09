import time
import unittest, os
import onkopus


class TestCLIAnnotation(unittest.TestCase):
#

    def test_cli_annotation(self):
        start = time.time()
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.vcf"
        outfile = infile + ".snv.anno.vcf"
        bframe = onkopus.read_file(infile)
        bframe.data = onkopus.annotate_variant_data(bframe.data, genome_version="hg19", include_clinical_data=False, include_gene=False, include_acmg=False)
        #print("Write annotated file in ",outfile)
        onkopus.write_file(outfile,bframe)
        stop = time.time() - start
        print("Required time: ",stop)

        with open(outfile, 'r') as file:
            read_content = file.read()

        content_exp=('ILTER\tINFO\n'
 'chr7\t21784211\t0\tA\tAG\t0\t0\t'
 '0;chrom=7;pos_hg38=21744593;pos_hg19=21784211;ref=A;alt=AG\n'
 'chr10')

        self.assertEqual(read_content[50:150], content_exp,"")

