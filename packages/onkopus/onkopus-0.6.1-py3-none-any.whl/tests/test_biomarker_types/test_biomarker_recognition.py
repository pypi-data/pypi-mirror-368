import unittest, os
import onkopus as op


class BiomarkerRecognitionTestCase(unittest.TestCase):

    def test_silent_mutation_recognition(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.hg38.ln200.vcf"
        # bframe = op.read_file(__location__ + "/../test_files/variants_grch38_20240206_Pathogenic_80.tsv")
        bframe = op.read_file(infile)
        genome_version="hg38"

        bframe.data = op.UTAAdapterClient(genome_version="hg38").process_data(bframe.data)
        bframe.data = op.CCSGeneToGenomicClient(genome_version=genome_version).process_data(
            bframe.data, data_type="g")

        for var in bframe.data.keys():
            #vartype = bframe.data[var]["type"]
            vstr = ""
            #print(vartype)
            if "UTA_Adapter" in bframe.data[var].keys():
                if "variant_exchange" in bframe.data[var]["UTA_Adapter"].keys():
                    vstr += var + ": "
                    vstr += bframe.data[var]["UTA_Adapter"]["variant_exchange"]
                    vstr += ":" + bframe.data[var]["mutation_type"]
                    print(vstr)

        self.assertIn("chr18:7888143G>A", list(bframe.data.keys()), f"chr18:7888143G>A is not in the list")
        self.assertEqual(bframe.data["chr18:7888143G>A"]["UTA_Adapter"]["variant_exchange"],"E78=","")

    def test_silent_mutation_annotation(self):
        data = {"chr18:7888143G>A": {}}

        data = op.annotate_variant_data(data)
        print(data)

        self.assertEqual(["chr18:7888143G>A"],list(data.keys()))




