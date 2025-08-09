import unittest
import os
import onkopus as op
import adagenes as ag


class TestCNAAnnotation(unittest.TestCase):

    def test_cna_annotation(self):
        data = { "chr15:30103918><DEL>":{ "variant_data": { "CHROM": 15, "POS":30103918, "POS2": 30644082 },"mutation_type": "cnv" }}
        bframe = ag.BiomarkerFrame(data)
        #print(bframe.data)
        data = op.annotate_cnas(bframe.data)
        #print(data)
        self.assertEqual(set(list(data["chr15:30103918><DEL>"].keys())),
                         {'type', 'gencode_cna', 'mdesc', 'variant_data', 'mutation_type','protein_domains', 'dgidb'},
                         "")
        self.assertEqual(len(data["chr15:30103918><DEL>"]["gencode_cna"]["cds"]),128,"")

    def test_cna_annotation_file(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/cnv_sample.vcf"
        bframe = op.read_file(infile, genome_version="hg38")
        #data = {"chr15:30103918><DEL>": {"variant_data": {"CHROM": 15, "POS": 30103918, "POS2": 30644082},
        #                                 "mutation_type": "cnv"}}
        #bframe = ag.BiomarkerFrame(data)
        #print(bframe.data)
        data = op.annotate_cnas(bframe.data)
        #print("annotated data ", data)

        self.assertEqual(set(list(data["chr1:258946A><DEL>"].keys())),
                         {'type', 'gencode_cna', 'mdesc', 'variant_data', 'mutation_type', 'protein_domains',
                          'info_features','orig_identifier', 'dgidb'},
                         "")
        self.assertEqual(len(data["chr1:258946A><DEL>"]["gencode_cna"]["cds"]), 2, "")
        self.assertEqual(data["chr1:258946A><DEL>"]["variant_data"]["POS2"], "714338", "")
