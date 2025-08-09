import unittest
import onkopus


class InterpreterTestCase(unittest.TestCase):

    def test_interpreter_client(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}, "chr12:25245350C>T": {}}

        variant_data = onkopus.onkopus_clients.uta_adapter_client.UTAAdapterClient(
            genome_version=genome_version).process_data(data)
        print("uta response", variant_data)

        client = onkopus.onkopus_clients.REVELClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        client = onkopus.onkopus_clients.MVPClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        client = onkopus.onkopus_clients.DBNSFPClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)

        variant_data = onkopus.onkopus_clients.InterpreterClient(
            genome_version=genome_version).process_data(variant_data, tumor_type="Melanoma")

        print("Interpreter response ",variant_data)
