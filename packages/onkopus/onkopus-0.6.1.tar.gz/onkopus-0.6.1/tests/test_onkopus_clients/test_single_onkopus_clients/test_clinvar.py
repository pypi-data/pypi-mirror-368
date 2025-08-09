import unittest, copy, os
import onkopus.onkopus_clients
import adagenes as ag


class ClinVarAnnotationTestCase(unittest.TestCase):

    def test_clinvar_client(self):
        genome_version = 'hg19'
        variant_data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}, "chr10:8115914C>.": {}}
        #variant_data = ag.LiftoverAnnotationClient(genome_version=genome_version, target_genome="hg38").process_data(variant_data)
        variant_data = ag.LiftoverClient(genome_version="hg19",target_genome="hg38").process_data(variant_data)
        variant_data = onkopus.onkopus_clients.ClinVarClient(
            genome_version=genome_version).process_data(variant_data)
        print("Response ",variant_data)
        #self.assertListEqual(["chr17:7681744T>C", "chr10:8115913C>T", "chr10:8115914C>."], list(variant_data.keys()), "")
        #self.assertEqual('0.00001',variant_data["chr10:8115913C>T"]["clinvar"]["AF_EXAC"],"")

    def test_clinvar_client_batch(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        input_file = __location__ + "/../../test_files/somaticMutations.vcf"
        genome_version = 'hg38'
        #onkopus.annotate_file(file, file+'.clinvar', 'clinvar', genome_version=genome_version)

        data = onkopus.read_file(input_file)

        data.data = onkopus.onkopus_clients.ClinVarClient(
            genome_version=genome_version).process_data(data.data)
        print(data.data)

    def test_clinvar_hg19(self):
        genome_version = 'hg19'
        variant_data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}, "chr10:8115914C>.": {}}
        bframe = ag.BiomarkerFrame(variant_data)
        #print("generated ",bframe.data)
        variant_data = ag.LiftoverAnnotationClient(genome_version=genome_version, target_genome="hg38").process_data(
            bframe.data)
        #print("var liftover ",variant_data)
        variant_data = onkopus.onkopus_clients.ClinVarClient(
            genome_version=genome_version).process_data(variant_data)
        #print("Response ",variant_data)
        self.assertListEqual(["chr17:7681744T>C", "chr10:8115913C>T", "chr10:8115914C>."], list(variant_data.keys()), "")
        self.assertEqual('0.00001',variant_data["chr10:8115913C>T"]["clinvar"]["AF_EXAC"],"")

    def test_clinvar_hg38(self):
        genome_version = 'hg38'
        variant_data = {"chr7:140753336A>T": {}}
        variant_data = onkopus.onkopus_clients.ClinVarClient(
            genome_version=genome_version).process_data(variant_data)
        print("Response ",variant_data)
        self.assertListEqual(["chr7:140753336A>T"], list(variant_data.keys()), "")
        self.assertEqual('0.00002',variant_data["chr7:140753336A>T"]["clinvar"]["AF_EXAC"],"")
