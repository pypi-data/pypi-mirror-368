import unittest, copy, os
import onkopus as op
import adagenes as ag

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

class DBSNPAnnotationTestCase(unittest.TestCase):

    def test_dbsnp_client(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}, "chr1:2556710C>A": {},
                "chr1:2556710C>T":{},"chr1:2556714A>G":{}, "chr1:2556718C>T":{},
                "chr1:2556718C>.": {}, "chr1:2556710C>.":{}
                }

        variant_data = op.DBSNPClient(
            genome_version=genome_version).process_data(data)

        print("Response ",variant_data)
        self.assertListEqual(["chr7:140753336A>T", "chr1:2556710C>A",
                "chr1:2556710C>T","chr1:2556714A>G", "chr1:2556718C>T",
                "chr1:2556718C>.", "chr1:2556710C>."], list(variant_data.keys()),
                             "")
        self.assertEqual('0:23038(0.0)', variant_data["chr1:2556710C>T"]["dbsnp"]["freq_total"], "")

    def test_dbsnp_file(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../../test_files/somaticMutations.hg38.ln200.vcf"
        outfile = __location__ + "/../../test_files/somaticMutations.hg38.ln200.dbsnp.vcf"

        # filter_data = ['pos', {'filterType': 'number', 'type': 'greaterThan', 'filter': 47742809}]
        filter_data = "dbsnp_total > 0.8"

        client = op.DBSNPClient(genome_version="hg38")

        ag.process_file(infile, outfile, client)

        with open(outfile, 'r') as file:
            actual_contents = file.read()

        expected_contents = ''

        # Compare the actual contents to the expected contents
        # self.assertEqual(actual_contents, expected_contents,
        #                 f"File contents do not match. Expected: {expected_contents}, Actual: {actual_contents}")
        self.assertEqual(file_len(outfile), 213)
