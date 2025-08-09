import unittest,os
import adagenes
import onkopus as op


class VariantDataExportTestCase(unittest.TestCase):

    def test_export_variant_data(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        data = {"chr7:140753336A>T":{}}
        genome_version = "hg38"
        bf = adagenes.BiomarkerFrame()

        bf.data = op.annotate_variant_data(data, genome_version="hg38")
        #print(data)

        outfile=__location__ + "/../test_files/test.out.csv"
        op.write_file(outfile, bf, file_type="csv")

