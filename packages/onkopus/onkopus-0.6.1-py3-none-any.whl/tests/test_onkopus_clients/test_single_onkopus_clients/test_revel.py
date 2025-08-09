import unittest, copy, os
import onkopus.onkopus_clients
import adagenes


class REVELAnnotationTestCase(unittest.TestCase):

    def test_revel_client(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}, "chr10:8115913C>T": {}}

        variant_data = onkopus.onkopus_clients.REVELClient(
            genome_version=genome_version).process_data(data)

        print("Response ",variant_data)

    def test_revel_client_file(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../../test_files/somaticMutations.ln50.vcf"
        outfile = __location__ + "/../../test_files/somaticMutations.ln50.revel.csv"
        bframe = adagenes.read_file(infile)
        genome_version = 'hg19'
        bframe = adagenes.LiftoverClient(genome_version=genome_version).process_data(bframe)
        bframe.data = onkopus.onkopus_clients.REVELClient(
            genome_version=genome_version).process_data(bframe.data)
        print(bframe.data)
        mapping = { "revel":"Score","variant_data":["CHROM","POS","REF","ALT"] }
        labels = {"revel":"revel_Score", "CHROM":"variant_data_CHROM", "POS":"variant_data_POS", "REF":"variant_data_REF", "ALT":"variant_data_ALT"}
        ranked_labels = ["CHROM","POS","REF","ALT","revel"]
        adagenes.write_file(outfile,bframe,mapping=mapping,labels=labels,ranked_labels=ranked_labels)
