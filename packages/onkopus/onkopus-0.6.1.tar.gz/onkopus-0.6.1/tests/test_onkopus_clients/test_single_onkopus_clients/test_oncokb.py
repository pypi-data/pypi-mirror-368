import unittest, os
import onkopus.onkopus_clients


class OncoKBAnnotationTestCase(unittest.TestCase):

    def test_oncokb_client(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}}
        key = os.getenv("ONCOKB_KEY")

        variant_data = onkopus.UTAAdapterClient(genome_version=genome_version).process_data(data)
        variant_data = onkopus.onkopus_clients.OncoKBClient(
            genome_version=genome_version).process_data(variant_data,key=key)

        if "oncokb" in variant_data["chr7:140753336A>T"]:
            print("Response ",variant_data["chr7:140753336A>T"]["oncokb"])

    #def test_oncokb_client_batch(self):
    #    __location__ = os.path.realpath(
    #        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    #    genome_version = 'hg19'
    #    file= __location__ + '/../../test_files/somaticMutations.vcf'
    #    data = onkopus.read_file(file)
    #    data.data = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version).process_data(data.data)
    #    data.data = onkopus.onkopus_clients.OncoKBClient(
    #        genome_version=genome_version).process_data(data.data)
    #    print(data.data)
