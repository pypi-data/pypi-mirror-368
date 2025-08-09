import unittest, os
import onkopus as op


class TestAnnotatedDataReader(unittest.TestCase):

    def test_read_annotated_data(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.ln50.avf"
        bframe = op.read_file(infile)

