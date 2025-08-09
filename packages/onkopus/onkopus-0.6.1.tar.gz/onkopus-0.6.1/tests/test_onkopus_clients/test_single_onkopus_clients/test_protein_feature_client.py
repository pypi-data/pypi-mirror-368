import unittest, os
import onkopus
import adagenes as ag


class ProteinFeaturesTestCase(unittest.TestCase):

    def test_protein_features_client_hg19(self):
        genome_version = 'hg19'
        data = {"chr7:140453136A>T": {}}
        data = ag.LiftoverAnnotationClient(genome_version=genome_version).process_data(data)
        data = onkopus.onkopus_clients.uta_adapter_client.UTAAdapterClient(
            genome_version=genome_version).process_data(data)
        data = onkopus.onkopus_clients.ProteinFeatureClient(
            genome_version=genome_version).process_data(data)
        self.assertEqual(data["chr7:140453136A>T"]["protein_features"]["RSA"], 0.0352112676056338, "")

    def test_protein_features_client(self):
        genome_version = 'hg38'
        data = {"chr7:140753336A>T": {}, "chr12:25245350C>T": {}}

        variant_data = onkopus.onkopus_clients.uta_adapter_client.UTAAdapterClient(
            genome_version=genome_version).process_data(data)
        print("uta response", variant_data)

        client = onkopus.onkopus_clients.REVELClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        client = onkopus.onkopus_clients.MVPClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        client = onkopus.onkopus_clients.DBNSFPClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        #variant_data = onkopus.InterpreterClient(genome_version="hg38").process_data(variant_data)

        variant_data = onkopus.onkopus_clients.ProteinFeatureClient(
            genome_version=genome_version).process_data(variant_data)

        print("Plot response ",variant_data)
        self.assertEqual(variant_data["chr7:140753336A>T"]["protein_features"]["RSA"],0.0352112676056338,"")

    def test_protein_features_client_batch(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        genome_version = 'hg19'
        file = __location__ + '/../../test_files/somaticMutations_brca_ln250.avf'

        bframe = onkopus.read_file(file, genome_version=genome_version)
        bframe = ag.LiftoverClient(genome_version=genome_version).process_data(bframe, target_genome="hg38")
        self.assertEqual(bframe.genome_version, "hg38","")
        genome_version = bframe.genome_version

        variant_data = onkopus.onkopus_clients.uta_adapter_client.UTAAdapterClient(
            genome_version=genome_version).process_data(bframe.data)
        #print("uta response", variant_data)

        client = onkopus.onkopus_clients.REVELClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        client = onkopus.onkopus_clients.MVPClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        client = onkopus.onkopus_clients.DBNSFPClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        # variant_data = onkopus.InterpreterClient(genome_version="hg38").process_data(variant_data)

        variant_data = onkopus.onkopus_clients.ProteinFeatureClient(
            genome_version=genome_version).process_data(variant_data)

        #print("Plot response ", variant_data)
        qid = "chr20:32430020C>A"
        print(variant_data[qid]["protein_features"])
        self.assertEqual(variant_data[qid]["protein_features"]["RSA"], 0.8529411764705882, "")
        self.assertEqual(variant_data[qid]["UTA_Adapter"]["gene_name"],"ASXL1", "")
        self.assertEqual(variant_data[qid]["UTA_Adapter"]["variant_exchange"], "P229T", "")

    def test_silent_mutation_protfeat(self):
        genome_version = "hg38"
        variant_data = { "chr1:930325C>T": {"UTA_Adapter": { "gene_name": "SAMD11", "variant_exchange": "I260=" } } }
        variant_data = onkopus.onkopus_clients.ProteinFeatureClient(
            genome_version=genome_version).process_data(variant_data)

        self.assertEqual(variant_data[ "chr1:930325C>T"]["protein_features"]["RSA"], 1.0, "")
