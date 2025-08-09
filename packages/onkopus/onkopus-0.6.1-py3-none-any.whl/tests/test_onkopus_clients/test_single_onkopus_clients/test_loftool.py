import unittest, copy, os
import onkopus.onkopus_clients

class LoFToolAnnotationTestCase(unittest.TestCase):

    def test_loftool_client(self):
        genome_version = 'hg19'

        data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}}

        variant_data = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version).process_data(data)
        variant_data = onkopus.onkopus_clients.LoFToolClient(
            genome_version=genome_version).process_data(variant_data)

        print("Response ",variant_data)

    def test_loftool_client_batch(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        genome_version = 'hg38'
        file= __location__ + '/../../test_files/somaticMutations.vcf'

        data = onkopus.read_file(file)

        data.data = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version).process_data(data.data)

        data.data = onkopus.onkopus_clients.LoFToolClient(
            genome_version=genome_version).process_data(data.data)

        print(data.data)
