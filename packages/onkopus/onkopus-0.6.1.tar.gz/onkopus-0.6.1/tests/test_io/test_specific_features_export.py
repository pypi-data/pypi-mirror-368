import unittest, os
import onkopus as op
import adagenes as ag


class SpecificFeaturesExportTestCase(unittest.TestCase):

    def test_specified_features_export(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + '/../test_files/somaticMutations.ln50.avf'
        outfile = open(__location__ + "/../test_files/somaticMutations.ln50.revel.csv", 'w')

        bframe = op.read_file(infile, genome_version="hg19")
        print("pre freatures ",bframe.preexisting_features)
        bframe = ag.LiftoverClient().process_data(bframe, target_genome="hg38")

        bframe.data = op.DBNSFPClient(genome_version="hg38").process_data(bframe.data)

        op.write_file(outfile, bframe, file_type="csv", export_features=["variant_data>CHROM","variant_data>POS", "variant_data>REF","variant_data>ALT", "dbnsfp>REVEL_score_aggregated_value"])
