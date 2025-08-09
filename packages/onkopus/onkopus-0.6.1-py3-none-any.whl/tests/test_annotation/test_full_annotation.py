import unittest
import os, time
import onkopus as op
import adagenes as ag


class TestFullAnnotation(unittest.TestCase):

    def test_full_annotation(self):
        start = time.time()
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.vcf"
        outfile = infile + ".anno.vcf"
        bframe = op.read_file(infile, genome_version="hg19")
        #bframe.data = onkopus.annotate_variant_data(bframe.data, genome_version="hg19", include_clinical_data=False)
        bframe = op.annotate(bframe)
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

        self.assertEqual(read_content[50:150], content_exp, "")


    def test_full_annotation_gene_and_cnv(self):
        #data = {"TP53":{ }, "chr7:140753336A>T": {}, "NRAS:Q61L": {} }
        #bframe = adagenes.BiomarkerFrame()
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        #bframe = op.read_file(__location__ + "/../test_files/variants_grch38_20240206_Pathogenic_80.tsv")
        bframe = ag.BiomarkerFrame({"TP53":{},
                                    "chr1:258946A><DEL>":{"variant_data":{
                                        "CHROM":"1",
                                        "POS": "258946",
                                        "POS2":5532775}}
                                    })
        bframe.genome_version="hg38"
        #bframe.data = data
        #print(bframe.data)

        bframe = op.annotate(bframe)

        set0 = set(list(bframe.data["TP53"].keys()))
        set1 = {'type', 'mutation_type', 'mdesc', 'cosmic', 'civic', 'dgidb', 'gencode', 'onkopus_aggregator',
                'UTA_Adapter'}
        self.assertEqual(set0, set1, "")

        #print(bframe.data["chr1:258946A><DEL>"].keys())
        set0 = set(list(bframe.data["chr1:258946A><DEL>"].keys()))
        set1 = {'type', 'mutation_type', 'mdesc', 'dgidb', 'gencode_cna', 'variant_data', 'protein_domains'}
        self.assertEqual(set0, set1, "")

