import unittest
import adagenes as ag
import onkopus as op


class TranscriptToGenomicTestCase(unittest.TestCase):

    def test_uta_adapter_transcripttogenomic_client(self):
        genome_version = 'hg38'
        data = {"NM_004985.5:c.35G>A": {}}
        bframe = ag.BiomarkerFrame(data)
        print(bframe.data)
        variant_data = op.TranscriptToGenomicClient(
            genome_version=genome_version).process_data(bframe.data)
        #variant_data = op.UTAAdapterClient(
        #    genome_version=genome_version).process_data(variant_data)
        #variant_data = op.CCSGeneToGenomicClient(
        #    genome_version=genome_version).process_data(variant_data)
        #print("Response ",variant_data["chr1:114713908T>A"]["UTA_Adapter"])
        print(bframe.data)
        qids = ['chr12:25245350C>T']
        self.assertListEqual(list(variant_data.keys()), qids, "Error UTA adapter GeneToGenomic")
        self.assertEqual(variant_data['chr12:25245350C>T']["mutation_type"],"snv","")

    def test_transcripttogenomic_client1(self):
        genome_version = 'hg38'
        data = {'NM_004985.5:C.35G>A': {'type': 'c', 'mutation_type': 'snv', 'mdesc': 'transcript_cdna'}}
        bframe = ag.BiomarkerFrame(data)
        print("start ",bframe)
        variant_data = op.TranscriptToGenomicClient(
            genome_version=genome_version).process_data(bframe.data)
        print("ok ",bframe.data)
        qids = ['chr12:25245350C>T']
        self.assertListEqual(list(variant_data.keys()), qids, "Error UTA adapter GeneToGenomic")
        self.assertEqual(variant_data['chr12:25245350C>T']["mutation_type"], "snv", "")


