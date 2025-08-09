import unittest
import onkopus as op


class ProteinFeaturesTestCase(unittest.TestCase):

    def test_pdb_client(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}, "chr12:25245350C>T": {}}

        variant_data = op.uta_adapter_client.UTAAdapterClient(
            genome_version=genome_version).process_data(data)
        print("uta response", variant_data)

        client = op.REVELClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        client = op.MVPClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        client = op.DBNSFPClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        #variant_data = onkopus.InterpreterClient(genome_version="hg38").process_data(variant_data)

        variant_data = op.PDBClient(
            genome_version=genome_version).process_data(variant_data["chr7:140753336A>T"])

    def test_pdb_client_protein(self):
        genome_version = 'hg38'

        data = {"ANKRD11:P2117L": {}}

        variant_data = op.CCSGeneToGenomicClient(genome_version=genome_version).process_data(data, data_type="p")
        variant_data = op.UTAAdapterClient(
                genome_version=genome_version).process_data(variant_data)
        print("uta response", variant_data)

        client = op.REVELClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        client = op.MVPClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        client = op.DBNSFPClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        # variant_data = onkopus.InterpreterClient(genome_version="hg38").process_data(variant_data)

        variant_data = op.PDBClient(
                genome_version=genome_version).process_data(variant_data[list(variant_data.keys())[0]])
        #print(variant_data)

        #print("Plot response ",variant_data[0]["data"]["PDB_file_string"])
        print(len(variant_data[0]["data"]["PDB_file_string"]))
        # print(variant_data[0]["data"]["PDB_file_string"],file=outfile)
        # outfile.close()
        self.assertEqual(len(variant_data[0]["data"]["PDB_file_string"]),1716146,"Error PDB retrieval")
