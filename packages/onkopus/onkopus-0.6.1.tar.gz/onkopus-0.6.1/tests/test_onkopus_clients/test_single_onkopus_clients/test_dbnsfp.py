import unittest, os
import onkopus.onkopus_clients
import onkopus as op
import adagenes

class DBNSFPAnnotationTestCase(unittest.TestCase):

    def test_dbnsfp_client(self):
        genome_version = 'hg38'
        data = {"chr10:8073950C>T": {}}

        data = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version).process_data(data)
        data = adagenes.LiftoverAnnotationClient(genome_version=genome_version).process_data(data)
        variant_data = onkopus.onkopus_clients.DBNSFPClient(
            genome_version=genome_version).process_data(data)

        self.assertEqual(str(variant_data["chr10:8073950C>T"]["dbnsfp"]["ALFA_European_AN"]), "9690",
                         "Value does not match")
        self.assertEqual(str(variant_data["chr10:8073950C>T"]["dbnsfp"]["FATHMM_score"]), "-4.08;.;-4.05",
                         "Value does not match")
        self.assertEqual(str(variant_data["chr10:8073950C>T"]["dbnsfp"]["MVP_score"]), "0.825523400301;.;0.825523400301",
                         "Value does not match")
        self.assertEqual(str(variant_data["chr10:8073950C>T"]["dbnsfp"]["AlphaMissense_pred"]), "B;.;B",
                         "Value does not match")
        self.assertEqual(str(variant_data["chr10:8073950C>T"]["dbnsfp"]["ESM1b_score"]), "-11.023;-11.023;-10.794",
                         "Value does not match")
        self.assertEqual(variant_data["chr10:8073950C>T"]["dbnsfp"]["AlphaMissense_score_aggregated_value"],"0.137","Value does not match")

    def test_dbnsfp_client_batch(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        genome_version = 'hg19'
        file= __location__ + '/../../test_files/somaticMutations_brca_ln250.avf'

        data = onkopus.read_file(file, genome_version=genome_version)
        data = adagenes.LiftoverClient(genome_version=genome_version).process_data(data, target_genome="hg38")
        data.data = onkopus.onkopus_clients.UTAAdapterClient(genome_version=data.genome_version).process_data(data.data)
        data.data = onkopus.onkopus_clients.DBNSFPClient(
            genome_version=data.genome_version).process_data(data.data)

        print("AM score ",data.data["chr10:8073950C>T"]["dbnsfp"]["AlphaMissense_score_aggregated_value"])

        #print(data.data["chr10:8073950C>T"]["dbnsfp"])
        self.assertEqual(str(data.data["chr10:8073950C>T"]["dbnsfp"]["ALFA_European_AN"]), "9690","Value does not match")
        self.assertEqual(str(data.data["chr10:8073950C>T"]["dbnsfp"]["FATHMM_score"]), "-4.08;.;-4.05",
                         "Value does not match")
        self.assertEqual(str(data.data["chr10:8073950C>T"]["dbnsfp"]["MVP_score"]), "0.825523400301;.;0.825523400301",
                         "Value does not match")
        self.assertEqual(str(data.data["chr10:8073950C>T"]["dbnsfp"]["AlphaMissense_pred"]), "B;.;B",
                         "Value does not match")
        self.assertEqual(str(data.data["chr10:8073950C>T"]["dbnsfp"]["ESM1b_score"]), "-11.023;-11.023;-10.794",
                         "Value does not match")
