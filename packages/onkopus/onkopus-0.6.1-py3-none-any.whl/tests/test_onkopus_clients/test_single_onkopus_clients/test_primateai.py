import unittest
import onkopus.onkopus_clients

class PrimateAIAnnotationTestCase(unittest.TestCase):

    def test_primateai_client(self):
        genome_version = 'hg19'

        data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}}
        data = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version).process_data(data)
        data = onkopus.onkopus_clients.LiftOverClient(genome_version=genome_version).process_data(data)
        variant_data = onkopus.onkopus_clients.PrimateAIClient(
            genome_version=genome_version).process_data(data)

        print("Response ",variant_data)

    #def test_primateai_client_batch(self):
    #    genome_version = 'hg19'
    #    file='../test_files/somaticMutations.l100.vcf'
    #    data = onkopus.read_file(file, genome_version=genome_version)
    #    data.data = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version).process_data(data.data)
    #    data.data = onkopus.onkopus_clients.LiftOverClient(genome_version=genome_version).process_data(data.data)
    #    data.data = onkopus.onkopus_clients.PrimateAIClient(
    #        genome_version=genome_version).process_data(data.data)
    #    print(data.data)
