import unittest, copy, os
import onkopus as op
import adagenes as ag

class UTAAdapterAnnotationTestCase(unittest.TestCase):

    def test_uta_adapter_client(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}}

        variant_data = op.UTAAdapterClient(
            genome_version=genome_version).process_data(data)

        self.assertEqual(variant_data["chr7:140753336A>T"]["UTA_Adapter"]["gene_name"],"BRAF")
        self.assertEqual(variant_data["chr7:140753336A>T"]["UTA_Adapter"]["variant"],"NP_004324.2:p.(Val600Glu)")
        self.assertEqual(variant_data["chr7:140753336A>T"]["UTA_Adapter"]["variant_exchange_long"],"Val600Glu")

    def test_uta_adapter_deletion(self):
        genome_version = 'hg38'

        data = {"chr15:25356042CTCTG>C": {"variant_data":{"CHROM":"15","POS":25356042,"REF":"CTCTG","ALT":"C"}}}
        bframe = ag.BiomarkerFrame(data)
        #print(bframe.data)

        variant_data = op.UTAAdapterClient(
            genome_version=genome_version).process_data(bframe.data)

        #self.assertEqual(variant_data["chr7:140753336A>T"]["UTA_Adapter"]["gene_name"],"BRAF")
        #self.assertEqual(variant_data["chr7:140753336A>T"]["UTA_Adapter"]["variant"],"NP_004324.2:p.(Val600Glu)")

    def test_uta_adapter_client_batch(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        genome_version = 'hg19'

        infile = __location__ + "/../../test_files/somaticMutations.vcf"

        bframe = op.read_file(infile,genome_version=genome_version)
        bframe = ag.LiftoverClient(bframe.genome_version).process_data(bframe,target_genome="hg38")
        bframe.data = op.onkopus_clients.UTAAdapterClient(
            genome_version=bframe.genome_version).process_data(bframe.data)

        print("Response ",bframe.data)
