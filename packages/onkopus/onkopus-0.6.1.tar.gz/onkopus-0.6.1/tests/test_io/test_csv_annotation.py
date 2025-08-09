import unittest, os
import onkopus as op
import adagenes as ag

class CSVAnnotationtestCase(unittest.TestCase):

    def test_annotate_with_additional_columns(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.revel.csv"
        bframe = op.read_file(infile, genome_version="hg38")
        #print("pre features ",bframe.preexisting_features)
        outfile = __location__ + "/../test_files/somaticMutations.revel.am.esm1b.csv"

        bframe.data = op.REVELClient(genome_version="hg38").process_data(bframe.data)
        bframe.data = op.DBNSFPClient(genome_version="hg38").process_data(bframe.data)

        for var in bframe.data.keys():
            if "AlphaMissense_score_aggregated_value" in bframe.data[var]["dbnsfp"].keys():
                print("found")

        op.write_file(outfile,bframe,export_features={"AlphaMissense":"dbnsfp>AlphaMissense_score_aggregated_value","REVEL":"revel>Score"})
