import unittest, copy
import onkopus.onkopus_clients
import adagenes, os


class LiftoverAnnotationTestCase(unittest.TestCase):

    def test_liftover_client(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        genome_version = 'hg19'

        #infile = "../test_files/somaticMutations.vcf"
        infile = __location__ + "/../../test_files/somaticMutations.vcf"
        outfile = __location__ + "/../../test_files/somaticMutations.tsv.liftover"
        data = adagenes.VCFReader(genome_version).read_file(infile)

        data.data = onkopus.onkopus_clients.LiftOverClient(
            genome_version=genome_version).process_data(data.data)

        print("Response ",data.data)



