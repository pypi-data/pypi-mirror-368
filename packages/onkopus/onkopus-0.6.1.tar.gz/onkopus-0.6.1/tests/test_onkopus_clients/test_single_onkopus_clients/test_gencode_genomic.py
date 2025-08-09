import unittest, copy, os
import onkopus as op
import adagenes as ag

class GencodeAnnotationTestCase(unittest.TestCase):

    def test_gencode_client(self):
        genome_version = 'hg19'

        data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}}

        variant_data = op.UTAAdapterClient(genome_version=genome_version).process_data(data)
        variant_data = op.LiftOverClient(genome_version=genome_version,target_genome="hg38").process_data(variant_data)
        genome_version="hg38"
        variant_data = op.GENCODEGenomicClient(
            genome_version=genome_version).process_data(variant_data)

        print("Response ",variant_data)

    def test_gencode_client_hg38(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}}

        variant_data = op.UTAAdapterClient(genome_version=genome_version).process_data(data)
        #variant_data = onkopus.onkopus_clients.LiftOverClient(genome_version=genome_version,target_genome="hg38").process_data(variant_data)
        variant_data = op.GENCODEGenomicClient(
            genome_version=genome_version).process_data(variant_data)

        print("Response ",variant_data)

    def test_gencode_client_vcf_export(self):
        genome_version = 'hg38'
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        outfile = __location__ + "/../../test_files/output_gencode_genomic.vcf"

        data = {"chr7:140753336A>T": {}}

        variant_data = op.UTAAdapterClient(genome_version=genome_version).process_data(data)
        variant_data = op.GENCODEGenomicClient(
            genome_version=genome_version).process_data(variant_data)
        op.write_file(outfile, variant_data)

        file = open(outfile)
        contents = file.read()[0:1000]
        contents_expected = """n"""
        print(contents)
        #self.assertEqual(contents, contents_expected, "")
        file.close()


