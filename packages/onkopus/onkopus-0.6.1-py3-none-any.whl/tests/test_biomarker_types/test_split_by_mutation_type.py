import unittest
import adagenes
import onkopus as op


class TestMutationType(unittest.TestCase):

    def test_split_by_mutation_type(self):

        data = { "chr7:140753336A>T": {}, "TP53": {}, "NRAS:Q61L":{} }
        bframe = adagenes.BiomarkerFrame(data=data,genome_version="hg38")
        data = adagenes.recognize_biomarker_types(bframe).data
        print(data)
        dc = op.split_data_by_mutation_type(data)
        print(dc)


