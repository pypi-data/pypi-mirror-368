import unittest, os
import onkopus as op

class TestOnkopusServer(unittest.TestCase):

    def test_onkopus_server_file_upload(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../../test_files/somaticMutations.ln50.vcf"
        outfile = __location__ + "/../../test_files/somaticMutations.ln50.revel.csv"
        client = op.OnkopusServerClient("hg38")
        client.interpret_variant_file(infile, "hg38")


