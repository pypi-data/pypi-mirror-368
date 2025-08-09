import unittest
import onkopus as op
import adagenes


class TestBiomarkerTypeConversion(unittest.TestCase):

    def test_protein_to_genomic(self):
        data = {"NRAS:Q61L": {}}
        bframe = adagenes.BiomarkerFrame(data, data_type="p")
        bframe = op.ProteinToGenomic().process_data(bframe)

        print(bframe)
        self.assertListEqual(list(bframe.data.keys()), ["chr1:114713908T>A"], "")

