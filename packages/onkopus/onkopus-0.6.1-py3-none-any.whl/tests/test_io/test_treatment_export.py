
import unittest,os
import adagenes
import onkopus as op


class TreatmentExportTestCase(unittest.TestCase):

    def test_export_treatment_data(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        oncokb_key = os.getenv("ONCOKB_KEY")

        data = {"chr7:140753336A>T":{}, "chr17:7673776G>A":{}}
        genome_version = "hg38"
        bf = adagenes.BiomarkerFrame(genome_version=genome_version,data=data)
        bf = op.annotate(bf, genome_version="hg38",oncokb_key=oncokb_key)

        outfile=__location__ + "/../test_files/test_writer.out.csv"
        op.ClinSigWriter().write_evidence_data_to_file(bf,outfile,sep="\t")

        file = open(outfile, 'r')
        contents = file.read()
        contents_expected = """biomarker\tcitation_i"""
        self.assertEqual(contents[0:20], contents_expected, "")
        file.close()



    def test_export_treatment_data_opened_file(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        oncokb_key = os.getenv("ONCOKB_KEY")

        data = {"chr7:140753336A>T":{}, "chr17:7673776G>A":{}}
        genome_version = "hg38"
        bf = adagenes.BiomarkerFrame(genome_version=genome_version,data=data)
        bf = op.annotate(bf, genome_version="hg38",oncokb_key=oncokb_key)
        bf.data = op.DrugOnClient(genome_version=genome_version).process_data(bf.data)

        #print(bf.data["chr7:140753336A>T"]["oncokb"])

        outfile_str=__location__ + "/../test_files/test_writer.out.stream.csv"
        outfile = open(outfile_str, "w")
        op.ClinSigWriter().write_evidence_data_to_file_all_features(bf,outfile=outfile,sep="\t")
        outfile.close()

        #file = open(outfile_str)
        #contents = file.read()

        with open(outfile_str, 'r') as file:
            contents = file.read()

        contents_expected = 'biomarker\tcitation_id\tcitation_url\tdisease\tdisease_normalized\tdrugs\t'\
 'evidence_level\tevidence_level_onkopus\tevidence_statement\tevidence_type\t'\
 'match_type\tmatch_type_str\tresponse\tscore\tsource\tsource_link\tsources\t'\
 'gene\tid\tpublication\tvariant_exchange\tUTA_Adapter.gene_name\t'\
 'UTA_Adapter.variant_exchange\tdrug_class\n'\
 '"BRAF V600E"\t"26678033"\t"http://www.ncbi.nlm.nih.gov/pubmed/26678033"\t'\
 '"Melanoma"\t"Melanoma"\t"S'
        self.assertEqual(contents[0:400], contents_expected, "")
        #file.close()

    def test_export_treatment_data_filestream(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        oncokb_key = os.getenv("ONCOKB_KEY")

        data = {"chr7:140753336A>T":{}, "chr17:7673776G>A":{}}
        genome_version = "hg38"
        bf = adagenes.BiomarkerFrame(genome_version=genome_version,data=data)
        bf = op.annotate(bf, genome_version="hg38",oncokb_key=oncokb_key)

        #print(bf.data["chr7:140753336A>T"]["oncokb"])

        import io
        import pandas as pd
        outfile_str=__location__ + "/../test_files/test_writer.out.stream.csv"
        outfile = io.StringIO()
        op.ClinSigWriter().write_evidence_data_to_file_all_features(bf,outfile=outfile,sep="\t")

        outfile.seek(0)
        df = pd.read_csv(outfile, sep="\t", names=range(12))
        #print("TREATMENTS ",df)
        outfile.close()



