import unittest
import onkopus as op


class ScanNetTestCase(unittest.TestCase):

    def test_bindingsite_client(self):
        genome_version = 'hg38'

        qid = "chr7:140753336A>T"
        data = {qid: {}, "chr12:25245350C>T": {}}

        variant_data = op.UTAAdapterClient(
            genome_version=genome_version).process_data(data)
        print("uta response", variant_data)

        #print(variant_data)
        #print("pdb ",pdb_data)
        gene = variant_data[qid]["UTA_Adapter"]["gene_name"]

        variant_data = op.ScanNetBindingSiteClient(
            genome_version=genome_version).process_data(gene)

        print("ScanNet response ",variant_data)


    def test_bindingsite_client_gene(self):
        genome_version = 'hg38'

        gene = "TMA7B"
        data = {gene: {"UTA_Adapter":{"gene_name": gene}}, }

        #variant_data =
        #variant_data = op.UTAAdapterClient(
        #    genome_version=genome_version).process_data(data)
        #print("uta response", variant_data)

        #pdb_data = op.PDBClient(
        #    genome_version=genome_version).process_data(variant_data[gene])

        #print(variant_data)
        #print("pdb ",pdb_data)
        #gene = variant_data[gene]["UTA_Adapter"]["gene_name"]

        variant_data = op.ScanNetBindingSiteClient(
            genome_version=genome_version).process_data(gene)

        print("ScanNet response ",variant_data)

