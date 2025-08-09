import unittest, copy
import adagenes
import onkopus.onkopus_clients

class MVPAnnotationTestCase(unittest.TestCase):

    def test_mvp_client(self):
        genome_version = 'hg19'

        #infile = "../test_files/somaticMutations.vcf"
        infile = "../test_files/somaticMutations.ln_12.vcf"
        outfile = "../test_files/somaticMutations.ln_12.tsv.mvp"
        #data = onkopus.VCFReader(genome_version).read_file(infile)

        #data.data = onkopus.onkopus_clients.MVPClient(
        #    genome_version=genome_version).process_data(data.data)

        #print("Response ",data.data)
        #mapping = { "variant_data": ["POS_hg19","POS_hg38"]
        #         }
        #onkopus.TSVWriter().write_to_file(outfile,data,mapping=mapping)

    def test_mvp_client_hg38(self):
        genome_version = 'hg38'
        data = {"chr7:140753336A>T": {}, "chr10:8073950C>T": {}}
        #for var in data:
        #    data[var] = onkopus.generate_variant_data_section(data[var])
        #print(data)

        #data = onkopus.onkopus_clients.LiftOverClient(genome_version=genome_version).process_data(data)
        data = adagenes.LiftoverClient(genome_version=genome_version).process_data(data)

        print(data)
        data = onkopus.onkopus_clients.MVPClient(
            genome_version=genome_version).process_data(data)

        print("Response ",data)


