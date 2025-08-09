import unittest
import onkopus as op
import adagenes as ag


class TestInDelAnnotationPipeline(unittest.TestCase):

    def test_indel_annotation(self):
        data = {"chr16:68846077C>CTTCAA":{}}
        data = op.indel_request(data)
        #print(data["chr16:68846077C>CTTCAA"]["clinvar"])
        print(data)

        #self.assertListEqual(list(data["chr16:68846077C>CTTCAA"].keys()),["variant_data","gencode_genomic","clinvar"],"Sections do not match")
        self.assertEqual(data["chr16:68846078_68846082insTTCAA"]["gencode_genomic"]["MANE_Select_transcript"],"ENST00000261778.2","")
        self.assertEqual(data["chr16:68846078_68846082insTTCAA"]["UTA_Adapter_indel"]["gene_name"],
                         "TANGO6", "")

    def test_short_indel(self):
        qid = "chr4:1802095insGGG"
        bframe = ag.BiomarkerFrame(qid)
        data = op.annotate(bframe)
        print(data)
