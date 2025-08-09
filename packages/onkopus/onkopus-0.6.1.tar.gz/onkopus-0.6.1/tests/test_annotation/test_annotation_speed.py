import unittest
import os, time
import onkopus as op
import adagenes as ag


class TestFullAnnotationSpeed(unittest.TestCase):

    def test_full_annotation_speed(self):
        start = time.time()
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.hg38.ln200.vcf"
        outfile = infile + ".anno.vcf"
        bframe = op.read_file(infile, genome_version="hg38")
        print("Variants ",len(list(bframe.data.keys())))
        #bframe.data = onkopus.annotate_variant_data(bframe.data, genome_version="hg19", include_clinical_data=False)
        bframe = op.annotate(bframe, )
        print(bframe.data.keys())
        op.write_file(outfile, bframe)
        stop = time.time() - start
        print("Required time: ", stop)

        with open(outfile, 'r') as file:
            read_content = file.read()

        content_exp = ('ILTER\tINFO\n'
 'chr7\t21744593\t0\tA\tAG\t0\t0\t'
 '0;chrom=chr7;pos_hg38=21744593;pos_hg19=21784211;ref=A;alt=AG\n'
 'ch')

        #self.assertEqual(read_content[50:150], content_exp, "")