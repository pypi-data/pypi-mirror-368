import unittest
import adagenes as ag
import onkopus as op


class IndelToGeneTestCase(unittest.TestCase):

    def test_uta_adapter_indeltogene_client(self):
        genome_version = 'hg38'
        data = {"chr16:68812175insTTCAA": {}}
        bframe = ag.BiomarkerFrame(data)
        print(bframe.data)
        variant_data = op.IndelToGeneClient(
            genome_version=genome_version).process_data(bframe.data)
        #variant_data = op.UTAAdapterClient(
        #    genome_version=genome_version).process_data(variant_data)
        #variant_data = op.CCSGeneToGenomicClient(
        #    genome_version=genome_version).process_data(variant_data)
        #print("Response ",variant_data["chr1:114713908T>A"]["UTA_Adapter"])
        print(bframe.data)
        qids = ["chr16:68812175insTTCAA"]
        self.assertListEqual(list(variant_data.keys()), qids, "Error UTA adapter IndelToGene")
        self.assertEqual(variant_data["chr16:68812175insTTCAA"]["UTA_Adapter_indel"]["gene_name"],"CDH1","")




